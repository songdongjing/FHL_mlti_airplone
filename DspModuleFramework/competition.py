
import competition_module as cm

class motion_interface(object):

	def init(self,json_data):
		self.module = cm.motion_imp();	
		self.module.init(json_data);

	def motion(self,json_data):    
		json_ret = self.module.motion(json_data);
		return json_ret; 

	def share(self,json_data):   
		json_ret = self.module.share(json_data);       
		return json_ret;  

class equipment_schedule_interface(object):			
		
	def eq_schedule(self,json_data,init_num,task_name):
		self.eq_load = cm.equipment_schedule_imp();
		json_ret = self.eq_load.eq_schedule(json_data,init_num,task_name);
		return json_ret; 
		
		
class consensus_interface(object):
	def consensus(self,json_data,task_name):
		self.consensus = cm.consensus_imp();
		
		json_ret = self.consensus.consensus(json_data,task_name);
		return json_ret; 
		