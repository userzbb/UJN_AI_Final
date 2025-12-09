import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

class SaveManager:
    DB_NAME = "saves.db"

    def __init__(self):
        self.db_path = os.path.join(os.getcwd(), self.DB_NAME)
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # 1. Save Metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS save_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                map_name TEXT,
                player_x INTEGER,
                player_y INTEGER
            )
        ''')

        # 2. Equipment
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                save_id INTEGER,
                slot TEXT,
                item_id TEXT,
                FOREIGN KEY(save_id) REFERENCES save_metadata(id)
            )
        ''')
        
        # 3. Player Stats (Placeholder for now)
        # cursor.execute(...)

        conn.commit()
        conn.close()

    def save_game(self, map_name: str, player_pos: tuple[int, int], equipment_slots: Dict[str, Optional[str]]) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert Metadata
        cursor.execute('''
            INSERT INTO save_metadata (timestamp, map_name, player_x, player_y)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, map_name, player_pos[0], player_pos[1]))
        
        save_id = cursor.lastrowid
        
        # Insert Equipment
        for slot, item_id in equipment_slots.items():
            if item_id:
                cursor.execute('''
                    INSERT INTO equipment (save_id, slot, item_id)
                    VALUES (?, ?, ?)
                ''', (save_id, slot, item_id))
        
        conn.commit()
        conn.close()
        return save_id

    def load_latest_save(self) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Get latest save
        cursor.execute('SELECT * FROM save_metadata ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
            
        save_id, timestamp, map_name, px, py = row
        
        # Get equipment
        cursor.execute('SELECT slot, item_id FROM equipment WHERE save_id = ?', (save_id,))
        equip_rows = cursor.fetchall()
        equipment = {slot: item_id for slot, item_id in equip_rows}
        
        conn.close()
        
        return {
            "id": save_id,
            "timestamp": timestamp,
            "map_name": map_name,
            "player_pos": (px, py),
            "equipment": equipment
        }

    def load_save_by_id(self, save_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM save_metadata WHERE id = ?', (save_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
            
        s_id, timestamp, map_name, px, py = row
        
        # Get equipment
        cursor.execute('SELECT slot, item_id FROM equipment WHERE save_id = ?', (s_id,))
        equip_rows = cursor.fetchall()
        equipment = {slot: item_id for slot, item_id in equip_rows}
        
        conn.close()
        
        return {
            "id": s_id,
            "timestamp": timestamp,
            "map_name": map_name,
            "player_pos": (px, py),
            "equipment": equipment
        }

    def list_saves(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT id, timestamp, map_name FROM save_metadata ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_save(self, save_id: int):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM equipment WHERE save_id = ?', (save_id,))
        cursor.execute('DELETE FROM save_metadata WHERE id = ?', (save_id,))
        conn.commit()
        conn.close()

    def update_save(self, save_id: int, map_name: str, player_pos: tuple[int, int], equipment_slots: Dict[str, Optional[str]]):
        conn = self._get_conn()
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update Metadata
        cursor.execute('''
            UPDATE save_metadata 
            SET timestamp = ?, map_name = ?, player_x = ?, player_y = ?
            WHERE id = ?
        ''', (timestamp, map_name, player_pos[0], player_pos[1], save_id))
        
        # Update Equipment (Delete old, insert new)
        cursor.execute('DELETE FROM equipment WHERE save_id = ?', (save_id,))
        
        for slot, item_id in equipment_slots.items():
            if item_id:
                cursor.execute('''
                    INSERT INTO equipment (save_id, slot, item_id)
                    VALUES (?, ?, ?)
                ''', (save_id, slot, item_id))
        
        conn.commit()
        conn.close()

# Global instance
save_manager = SaveManager()
