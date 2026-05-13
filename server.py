#!/usr/bin/env python3
"""
Civil Registry Search Server
Optimized SQLite patterns for high-performance web serving
"""
import sqlite3
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from contextlib import contextmanager

DB_FILE = "/run/media/defrag01/944CA94F4CA92D44/Users/DeFrag01/Documents/Gjendja Civile 2008/civil_registry_clean.db"

# Singleton connection with proper SQLite patterns
class ConnectionManager:
    _instance = None
    _conn = None
    
    @classmethod
    def get_connection(cls):
        if cls._conn is None:
            cls._conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=30.0)
            cls._conn.row_factory = sqlite3.Row
            # WAL mode for concurrent reads
            cls._conn.execute("PRAGMA journal_mode=WAL")
            # Better performance
            cls._conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
            cls._conn.execute("PRAGMA temp_store=MEMORY")
            cls._conn.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
            cls._conn.execute("PRAGMA synchronous=NORMAL")
        return cls._conn
    
    @classmethod
    def close(cls):
        if cls._conn:
            cls._conn.close()
            cls._conn = None

@contextmanager
def get_db():
    """Context manager for database connections - ensures proper cleanup"""
    conn = ConnectionManager.get_connection()
    try:
        yield conn
    except sqlite3.OperationalError as e:
        if "locked" in str(e):
            # Retry once on lock
            import time
            time.sleep(0.1)
            yield conn
        else:
            raise

class CivilRegistryHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/search':
            try:
                params = parse_qs(parsed.query)
                query = params.get('q', [''])[0].strip()
                page = int(params.get('page', ['1'])[0])
                limit = min(int(params.get('limit', ['50'])[0]), 100)
                
                results, total = self.search(query, page, limit)
                self.send_json({'results': results, 'total': total, 'page': page, 'pages': (total + limit - 1) // limit})
            except Exception as e:
                self.send_json({'error': str(e)}, status=500)
            
        elif parsed.path == '/api/person':
            params = parse_qs(parsed.query)
            person_id = params.get('id', [''])[0]
            result = self.get_person(person_id)
            self.send_json(result)
            
        elif parsed.path == '/api/stats':
            stats = self.get_stats()
            self.send_json(stats)
            
        elif parsed.path == '/api/suggest':
            params = parse_qs(parsed.query)
            query = params.get('q', [''])[0].strip()
            suggestions = self.get_suggestions(query)
            self.send_json({'suggestions': suggestions})
            
        elif parsed.path == '/' or parsed.path == '/index.html':
            self.serve_html()
        else:
            self.send_error(404)
    
    def search(self, query, page, limit):
        offset = (page - 1) * limit
        
        with get_db() as conn:
            cur = conn.cursor()
            
            if query:
                term = query.strip()
                
                sql = '''
                    SELECT l.Id, l.Emer, l.Mbiemer, l.Atesi, l.Amesi, l.Dtlindja, l.Vlindja,
                           s.Seksi, g.GjCivile, k.Kombesia, q.Qyteti, li.LidhjaKryef,
                           l.Adresa, l.NrBaneses, l.KryefId, l.EmriRegj, l.NrRegj
                    FROM tblLista_fts f
                    JOIN tblLista l ON l.Id = f.rowid
                    LEFT JOIN tblSeksi s ON l.IdSeksi = s.IdSeksi
                    LEFT JOIN tblGjCivile g ON l.IdGjCivile = g.IdGjCivile
                    LEFT JOIN tblKombesia k ON l.IdKombesia = k.IdKombesia
                    LEFT JOIN tblQyteti q ON l.IdQyteti = q.IdQyteti
                    LEFT JOIN tblLidhja li ON l.IdLidhja = li.IdLidhja
                    WHERE tblLista_fts MATCH ?
                    ORDER BY l.Mbiemer COLLATE NOCASE, l.Emer COLLATE NOCASE
                    LIMIT ? OFFSET ?
                '''
                params = [term, limit, offset]
            else:
                sql = '''
                    SELECT l.Id, l.Emer, l.Mbiemer, l.Atesi, l.Amesi, l.Dtlindja, l.Vlindja,
                           s.Seksi, g.GjCivile, k.Kombesia, q.Qyteti, li.LidhjaKryef,
                           l.Adresa, l.NrBaneses, l.KryefId, l.EmriRegj, l.NrRegj
                    FROM tblLista l
                    LEFT JOIN tblSeksi s ON l.IdSeksi = s.IdSeksi
                    LEFT JOIN tblGjCivile g ON l.IdGjCivile = g.IdGjCivile
                    LEFT JOIN tblKombesia k ON l.IdKombesia = k.IdKombesia
                    LEFT JOIN tblQyteti q ON l.IdQyteti = q.IdQyteti
                    LEFT JOIN tblLidhja li ON l.IdLidhja = li.IdLidhja
                    ORDER BY l.Mbiemer COLLATE NOCASE, l.Emer COLLATE NOCASE
                    LIMIT ? OFFSET ?
                '''
                params = [limit, offset]
            
            cur.execute(sql, params)
            rows = cur.fetchall()
            
            if query:
                cur.execute('SELECT COUNT(*) FROM tblLista_fts WHERE tblLista_fts MATCH ?', (term,))
            else:
                cur.execute('SELECT COUNT(*) FROM tblLista')
            total = cur.fetchone()[0]
            
            results = [{
                'id': r['Id'],
                'emer': r['Emer'] or '',
                'mbiemer': r['Mbiemer'] or '',
                'atesi': r['Atesi'] or '',
                'amesi': r['Amesi'] or '',
                'dtlindja': r['Dtlindja'] or '',
                'vlindja': r['Vlindja'] or '',
                'seksi': r['Seksi'] or '',
                'gjCivile': r['GjCivile'] or '',
                'kombesia': r['Kombesia'] or '',
                'qyteti': r['Qyteti'] or '',
                'lidhja': r['LidhjaKryef'] or '',
                'adresa': r['Adresa'] or '',
                'nrBaneses': r['NrBaneses'],
                'kryefId': r['KryefId'] or '',
                'emriRegj': r['EmriRegj'] or '',
                'nrRegj': r['NrRegj'] or ''
            } for r in rows]
            
            return results, total
    
    def get_person(self, person_id):
        try:
            person_id = int(person_id)
        except:
            return {'error': 'Invalid person ID'}
        
        with get_db() as conn:
            cur = conn.cursor()
            
            # Get person with all lookup data in single optimized query
            cur.execute('''
                SELECT l.*, s.Seksi, g.GjCivile, k.Kombesia, q.Qyteti, li.LidhjaKryef
                FROM tblLista l
                LEFT JOIN tblSeksi s ON l.IdSeksi = s.IdSeksi
                LEFT JOIN tblGjCivile g ON l.IdGjCivile = g.IdGjCivile
                LEFT JOIN tblKombesia k ON l.IdKombesia = k.IdKombesia
                LEFT JOIN tblQyteti q ON l.IdQyteti = q.IdQyteti
                LEFT JOIN tblLidhja li ON l.IdLidhja = li.IdLidhja
                WHERE l.Id = ?
            ''', (person_id,))
            row = cur.fetchone()
            
            if not row:
                return {'error': 'Person not found'}
            
            # Build person dict efficiently
            person = {key: (row[key] if row[key] is not None else '') for key in row.keys()}
            
            kryef_id = row['KryefId']
            
            # Get family members with KryefId index lookup
            if kryef_id:
                cur.execute('''
                    SELECT l.Id, l.Emer, l.Mbiemer, l.Atesi, l.Amesi, li.LidhjaKryef as Lidhja
                    FROM tblLista l
                    LEFT JOIN tblLidhja li ON l.IdLidhja = li.IdLidhja
                    WHERE l.KryefId = ?
                    ORDER BY l.IdLidhja
                ''', (kryef_id,))
                person['family'] = [dict(r) for r in cur.fetchall()]
            else:
                person['family'] = []
            
            # Use person's own Atesi/Amesi fields for birth parents
            # These contain the actual biological parents from birth records
            atesi_name = row['Atesi'] or ''
            amesi_name = row['Amesi'] or ''
            
            # Father: find person matching Atesi name
            # Look for IdLidhja=1 (Kryefamiljar) with matching name first, then any match
            person['father'] = None
            person['father_name'] = atesi_name
            if atesi_name:
                # Try to find clickable father by name in same family
                cur.execute('''
                    SELECT Id, Emer, Mbiemer, Atesi, Amesi FROM tblLista
                    WHERE KryefId = ? AND IdLidhja = 1
                    LIMIT 1
                ''', (kryef_id,))
                head = cur.fetchone()
                if head and f"{head['Emer']} {head['Mbiemer']}".upper() == atesi_name.upper():
                    person['father'] = {
                        'id': head['Id'], 
                        'emer': head['Emer'], 
                        'mbiemer': head['Mbiemer'],
                        'atesi': head['Atesi'] or '',
                        'amesi': head['Amesi'] or ''
                    }
            
            # Mother: find person matching Amesi name
            # Look for spouse (IdLidhja=2) with matching name, OR parent records (IdLidhja=28/29)
            person['mother'] = None
            person['mother_name'] = amesi_name
            if amesi_name:
                # Check if spouse has matching name (she would be the mother)
                cur.execute('''
                    SELECT Id, Emer, Mbiemer, Atesi, Amesi FROM tblLista
                    WHERE KryefId = ? AND IdLidhja = 2
                    LIMIT 1
                ''', (kryef_id,))
                spouse = cur.fetchone()
                if spouse and f"{spouse['Emer']} {spouse['Mbiemer']}".upper() == amesi_name.upper():
                    person['mother'] = {
                        'id': spouse['Id'], 
                        'emer': spouse['Emer'], 
                        'mbiemer': spouse['Mbiemer'],
                        'atesi': spouse['Atesi'] or '',
                        'amesi': spouse['Amesi'] or ''
                    }
                # Also check for parent records (IdLidhja=29 = E ëma / Mother)
                elif not person['mother']:
                    cur.execute('''
                        SELECT Id, Emer, Mbiemer, Atesi, Amesi FROM tblLista
                        WHERE KryefId = ? AND IdLidhja = 29
                        LIMIT 1
                    ''', (kryef_id,))
                    parent_mom = cur.fetchone()
                    if parent_mom and f"{parent_mom['Emer']} {parent_mom['Mbiemer']}".upper() == amesi_name.upper():
                        person['mother'] = {
                            'id': parent_mom['Id'], 
                            'emer': parent_mom['Emer'], 
                            'mbiemer': parent_mom['Mbiemer'],
                            'atesi': parent_mom['Atesi'] or '',
                            'amesi': parent_mom['Amesi'] or ''
                        }
            
            return person
    
    def get_suggestions(self, query):
        if not query or len(query) < 2:
            return []
        
        with get_db() as conn:
            cur = conn.cursor()
            
            cur.execute('''
                SELECT DISTINCT Mbiemer, COUNT(*) as cnt
                FROM tblLista
                WHERE Mbiemer LIKE ? COLLATE NOCASE
                GROUP BY Mbiemer
                ORDER BY cnt DESC
                LIMIT 5
            ''', (f'{query}%',))
            
            return [{'type': 'surname', 'value': row['Mbiemer'], 'count': row['cnt']} for row in cur.fetchall()]
    
    def get_stats(self):
        with get_db() as conn:
            cur = conn.cursor()
            
            stats = {}
            cur.execute('SELECT COUNT(*) FROM tblLista')
            stats['total'] = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(DISTINCT Mbiemer) FROM tblLista WHERE Mbiemer IS NOT NULL AND Mbiemer != ''")
            stats['uniqueLastNames'] = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(DISTINCT Emer) FROM tblLista WHERE Emer IS NOT NULL AND Emer != ''")
            stats['uniqueFirstNames'] = cur.fetchone()[0]
            
            return stats
    
    def send_json(self, data, status=200):
        response = json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)
    
    def serve_html(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = base_dir + '/index.html'
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404)

def run(port=8080):
    server = HTTPServer(('0.0.0.0', port), CivilRegistryHandler)
    print(f"Server started on port {port}")
    try:
        server.serve_forever()
    finally:
        ConnectionManager.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    run(port)