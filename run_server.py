import sys, os
sys.path.insert(0, r'C:\Users\sebad\Desktop\UTN\Profe Juan\Parcial\sdd-parcial1-gestion')
os.chdir(r'C:\Users\sebad\Desktop\UTN\Profe Juan\Parcial\sdd-parcial1-gestion')
import uvicorn
uvicorn.run('backend.main:app', host='0.0.0.0', port=8001, log_level='debug')
