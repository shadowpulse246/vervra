import os,tempfile,unittest
from app import create_app,socketio
from app import config
class Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); config.DATA_DIR=__import__('pathlib').Path(self.t.name);config.USERS_FILE=config.DATA_DIR/'users.json';config.SERVERS_DIR=config.DATA_DIR/'servers';self.app=create_app({'TESTING':True,'SECRET_KEY':'test'});self.c=self.app.test_client()
 def test_flow(self):
  self.assertEqual(self.c.post('/api/signup',json={'username':'alice','password':'password123'}).status_code,201);self.assertEqual(self.c.post('/api/signup',json={'username':'alice','password':'password123'}).status_code,400);sid=self.c.post('/api/servers',json={'name':'Town'}).json['server']['id'];self.assertEqual(self.c.get('/api/servers/'+sid).status_code,200);self.assertEqual(self.c.get('/api/servers/not-valid').status_code,404)
 def test_socket(self):
  self.c.post('/api/signup',json={'username':'alice','password':'password123'});sid=self.c.post('/api/servers',json={'name':'Town'}).json['server']['id'];x=socketio.test_client(self.app,flask_test_client=self.c);x.emit('join-server',{'server_id':sid});x.emit('join-room',{'server_id':sid,'room_id':'general'});x.emit('send-chat-message',{'server_id':sid,'room_id':'general','message':'hello'});self.assertTrue(any(e['name']=='chat-message' for e in x.get_received()))
if __name__=='__main__':unittest.main()
