import retroBot.config
import psycopg2
from psycopg2 import sql

def main():
    config = retroBot.config.config('config.yaml')
    channels = []
    with open(config['twitch']['channel_file'], 'r') as f:
        for i in f.readlines():
            channels.append(i.strip())
    for channel in channels:
        channel = channel.lower()
        conn = psycopg2.connect(f"dbname={config['postgres']['dbname']} user={config['postgres']['username']} host={config['postgres']['host']} port={config['postgres']['port']} password={config['postgres']['password']}")
        cur = conn.cursor()
        cmd = sql.SQL('INSERT INTO {}.{} SELECT %s, * FROM {}.{}').format(sql.Identifier(f'twitchlogger'), sql.Identifier(f'chat'), sql.Identifier(f'twitchlogger'), sql.Identifier(f'_{channel}'))
        cur.execute(cmd, (channel,))
        conn.commit()
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()