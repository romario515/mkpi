import sqlite3
import datetime


class BotDBWorker:
    def __init__(self, database):
        self.db = database

    def become_admin(self, chat_id):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        cursor.execute('insert into admins (chat_id) values (?)', (chat_id,))
        connection.commit()
        connection.close()

    def get_admin_list(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        admins = cursor.execute('select chat_id from admins').fetchall()
        connection.close()
        return tuple(x[0] for x in admins)

    def add_song_to_playlist(self, song):
        status = True
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        if cursor.execute('select * from playlist where song = ?', (song,)).fetchone():
            status = False
        cursor.execute('insert into playlist (song) values (?)', (song,))
        connection.commit()
        connection.close()
        return status

    def get_playlist(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        playlist = cursor.execute('select * from playlist').fetchall()
        cursor.execute('update playlist set is_new = 0 where is_new = 1')
        connection.commit()
        connection.close()
        return playlist


    def add_new_group(self, group):
        status = True
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        if cursor.execute('select * from groups where name = ?', (group,)).fetchone():
            status = False
        cursor.execute('insert into groups (name) values (?)', (group,))
        connection.commit()
        connection.close()
        return status

    def get_all_groups(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        groups = cursor.execute('select * from groups').fetchall()
        connection.close()
        return groups

    def get_group_by_name(self, name):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        group = cursor.execute('select * from groups where name = ?', (name,)).fetchone()
        connection.close()
        return group

    def delete_group_by_name(self, name):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        cursor.execute('delete from groups where name = ?', (name, )).fetchall()
        connection.commit()
        connection.close()

    def update_kcoins(self, group_id, kcoins):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        cursor.execute('update groups set coins = ? where id = ?', (kcoins, group_id))
        connection.commit()
        connection.close()
    
    def get_work_status_left(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        left = cursor.execute('SELECT pos_name, status FROM pos_history where pos_name = "left" ORDER BY ID DESC LIMIT 1' ).fetchone()
        connection.close()
        return left
    
    def get_work_status_right(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        right = cursor.execute('SELECT pos_name, status FROM pos_history where pos_name = "right" ORDER BY ID DESC LIMIT 1' ).fetchone()
        connection.close()
        return right
    
    def get_day_stat(self, status, pos):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        time= datetime.datetime.now().strftime("%Y-%m-%d")
        #print(status,time+'%',pos)
        right = cursor.execute('SELECT count(id) FROM pos_history where status = ? and timeserver like ? and pos_name=?', (status,time+'%',pos)).fetchone()
        #print('Должы получить число')
        #print(right[0])
        connection.close()
        return right[0]
    


    def sort_history_left(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        # Todo изначально предполагается "простой" поэтому добавить его первым
        oldstat='prostoy'
        st_time = '00:00'
        video_name_old= ''
        #Костыль на костыле но работает )
        count=3
        data = cursor.execute('SELECT * FROM pos_history where pos_name="left"').fetchall()
        #print (data)
        for id, pos_name, status,video_name,timeserver,t_fst in data:
            if status != oldstat and count==3:
                st_time=t_fst
                video_name_old= video_name
                count-=1
            if status != oldstat:
                count-=1
            
            if count == 0:
            #вставляем в базу начало нового этапа с временем из st_time
                count=3
                oldstat=status
                cursor.execute('insert into history_sorted ( "pos_name", "stat", "source", "time_start") values (?,?,?,?)',(pos_name,status,video_name_old,st_time))
                #print(pos_name,status,video_name_old,st_time)
            if status==oldstat and count<3 :
                count+=1
        connection.commit()  
        connection.close()
    
    def sort_history_right(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
            # Todo изначально предполагается "простой" поэтому добавить его первым
        oldstat='prostoy'
        st_time = '00:00'
        video_name_old= ''
        #Костыль на костыле но работает )
        count=3
        data = cursor.execute('SELECT * FROM pos_history where pos_name="right"').fetchall()
        #print (data)
        for id, pos_name, status,video_name,timeserver,t_fst in data:
            if status != oldstat and count==3:
                st_time=t_fst
                video_name_old= video_name
                count-=1
            if status != oldstat:
                count-=1
            
            if count == 0:
            #вставляем в базу начало нового этапа с временем из st_time
                count=3
                oldstat=status
                cursor.execute('insert into history_sorted ( "pos_name", "stat", "source", "time_start") values (?,?,?,?)',(pos_name,status,video_name_old,st_time))
                #print(pos_name,status,video_name_old,st_time)
            if status==oldstat and count<3 :
                count+=1
        connection.commit()  
        connection.close()


    def get_sorted_history_right(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        right = cursor.execute('SELECT stat,time_start FROM history_sorted where pos_name = "right" ORDER BY time_start ').fetchall()
        connection.close()
        return right
    def get_sorted_history_left(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        left = cursor.execute('SELECT stat,time_start FROM history_sorted where pos_name = "left" ORDER BY time_start ').fetchall()
        connection.close()
        return left
    
