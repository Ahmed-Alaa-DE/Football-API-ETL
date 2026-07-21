import os
import pandas as pd
import requests 
from dotenv import load_dotenv
import pyodbc


load_dotenv()




def get_and_transform_standings():

    print("\n---start ETL Process (Extract & Transform ) ---")

    url = "https://v3.football.api-sports.io/standings"


    api_key = os.getenv('API_KEY')
    if not api_key :
        raise ValueError("API_key not found !")

    headers = {'x-apisports-key' : api_key}

    query_params = {
            'league' : 2,
            'season' : 2023
            }
    

    try :

        response = requests.get(url , headers = headers , params=query_params)

        data = response.json()

        flat_standings = []

        for item in data['response'][0]['league']['standings'][0]:
            team_data = {
                'rank': item['rank'],
                'team_name' : item['team']['name'],
                'team_id' : item['team']['id'],
                'points' : item['points'],
                'goalsDiff': item['goalsDiff'],
                'form': item.get('form','N/A'),
                'group': item['group'],
                'played' : item['all']['played'],
                'win' : item['all']['win'],
                'lose' : item['all']['lose'],
                'draw': item['all']['draw'],
                'goals_for': item['all']['goals']['for'],
                'goals_against' : item['all']['goals']['against']
            }

            flat_standings.append(team_data)
        df = pd.DataFrame(flat_standings)
        print("Transformed Successfully")
        
        return df
        

    except requests.exceptions.RequestException as req_err :
        print (f"network or API error : {req_err}")
        return None

    except (IndexError , KeyError) as parse_err :
        print (f"data structure error (Key/Index missing): {parse_err}")
        return None

    except  Exception as e :
        print(f"An error occured : {e}")
        return None

        
    





def load_to_sql(df):
    if df is None or df.empty:
        print("No data to load !")
        return False
    print("Start Loading Data to SQL Server")

    conn = None
    try :
        conn_str = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost\\SQLEXPRESS;"
            "Database=Football_DP;"
            "Trusted_Connection=yes;"
        )

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        print("Connected Successfully !")

        insert_query = """INSERT INTO standings (
        [rank] , team_name ,	team_id,	points,	goalsDiff,	form,	[group],	played,	win,	lose,	draw,	goals_for,	goals_against) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)

        """ 


        rows_inserted = 0 
        cursor.execute("TRUNCATE TABLE standings")
        for index , row in df.iterrows():
            values = (
                int(row['rank']),
                str(row['team_name']),
                int(row['team_id']),
                int(row['points']),
                int(row['goalsDiff']),
                str(row['form']) if row['form'] != 'N/A' else None,
                str(row['group']),
                int(row['played']),
                int(row['win']),
                int(row['lose']),
                int(row['draw']),
                int(row['goals_for']),
                int(row['goals_against']),
            )

        
            cursor.execute(insert_query , values)
            rows_inserted += 1


        
        conn.commit()
        print(f"{rows_inserted} are successfully loaded into 'standings' table")
        return True




    except pyodbc.Error as conn_err :
        print(f"Connection Error Ocurred : {conn_err}")
        if conn:
            conn.rollback()


    finally:
        if conn:
            conn.close()
            print(" Database connection closed safely.")







if __name__ = "__main__" :

    df_clean = get_and_transform_standings()

    if df_clean is not None:
        load_to_sql(df_clean)

