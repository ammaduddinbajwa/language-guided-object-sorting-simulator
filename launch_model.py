"""Keep interactive API credentials out of source files and shell history."""
import getpass,os,runpy
from pathlib import Path
if __name__=='__main__':
 model=input('API model ID (supports structured outputs and images): ').strip()
 key=getpass.getpass('OpenAI API key (hidden; not saved): ').strip()
 if not model or not key:raise SystemExit('Model and key are required.')
 os.environ['OPENAI_MODEL']=model;os.environ['OPENAI_API_KEY']=key
 runpy.run_path(str(Path(__file__).with_name('server.py')),run_name='__main__')
