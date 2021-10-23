from ir_env import env_base
from ir_env import mobile_robot
from math import pi, cos, sin
import numpy as np

class env_robot(env_base):
    def __init__(self, world_name, robot_num=1, plot=True, **kwargs):
        super(env_robot, self).__init__(world_name, robot_num, plot=plot, **kwargs)
        self.random_bear = True

    def initialization(self, init_mode=1, **kwargs):

        # init_mode: 0 manually initialize
        #            1 single row
        #            2 random
        #            3 circular 
        # kwargs: random_bear random radius
        # 
        if init_mode == 0:
            if len(self.robot_radius_list) < self.robot_num:
                print('wrong number of robots')
        else:
            self.init_state_list, self.goal_list, self.robot_radius_list = self.init_state_distribute(init_mode, **kwargs)
        
        self.cur_mode = init_mode

        # robot
        for i in range(self.robot_num):
            robot = mobile_robot(id=i, mode=self.robot_mode, radius=self.robot_radius_list[i], init_state=self.init_state_list[i], goal=self.goal_list[i], vel_max = self.robot_vel_max, step_time=self.step_time, radius_exp=self.radius_exp, **kwargs)
            self.robot_list.append(robot)
            self.robot = robot if i == 0 else None

    def init_state_distribute(self, init_mode=1, interval=1, radius=0.2, square=[0, 0, 10, 10], circular=[5, 5, 4],  **kwargs):
        # init_mode: 1 single row
        #            2 random
        #            3 circular      
        # square area: x_min, y_min, x_max, y_max
        # circular area: x, y, radius
    
        self.random_bear = kwargs.get('random_bear', False)
        random_radius = kwargs.get('random_radius', False)

        num = self.robot_num
        state_list, goal_list = [], []

        if init_mode == 1:
             # single row
            state_list = [np.array([ [i * interval], [square[1]], [pi/2] ]) for i in range(int(square[0]), int(square[0])+num)]
            goal_list = [np.array([ [i * interval], [square[3]] ]) for i in range(int(square[0]), int(square[0])+num)]
            goal_list.reverse()

        elif init_mode == 2:
            # random
            state_list, goal_list = self.random_start_goal(interval, square)

        elif init_mode == 3:
            # circular
            circle_point = np.array(circular)
            theta_step = 2*pi / num
            theta = 0

            while theta < 2*pi:
                state = circle_point + np.array([ cos(theta) * circular[2], sin(theta) * circular[2], theta + pi- circular[2] ])
                goal = circle_point[0:2] + np.array([cos(theta+pi), sin(theta+pi)]) * circular[2]
                theta = theta + theta_step
                state_list.append(state[:, np.newaxis])
                goal_list.append(goal[:, np.newaxis])

        elif init_mode == 4:
            # random 2
            circle_point = np.array(circular)
            theta_step = 2*pi / num
            theta = 0

            while theta < 2*pi:
                state = circle_point + np.array([ cos(theta) * circular[2], sin(theta) * circular[2], theta + pi- circular[2] ])
                goal = circle_point[0:2] + np.array([cos(theta+pi), sin(theta+pi)]) * circular[2]
                theta = theta + theta_step
                state_list.append(state[:, np.newaxis])
                goal_list.append(goal[:, np.newaxis])

        elif init_mode == 5:
            
            half_num = int(num /2)

            state_list1 = [np.array([ [i * interval], [square[1]], [pi/2] ]) for i in range(int(square[0]), int(square[0])+half_num)]

            state_list2 = [np.array([ [i * interval], [square[3]], [pi/2] ]) for i in range(int(square[0]), int(square[0])+half_num)]
            state_list2.reverse()
            
            goal_list1 = [np.array([ [i * interval], [square[3]], [pi/2] ]) for i in range(int(square[0]), int(square[0])+half_num)]
            goal_list1.reverse()

            goal_list2 = [np.array([ [i * interval], [square[1]], [pi/2] ]) for i in range(int(square[0]), int(square[0])+half_num)]
            
            state_list, goal_list = state_list1+state_list2, goal_list1+goal_list2
                    
        if self.random_bear:
            for state in state_list:
                state[2, 0] = np.random.uniform(low = -pi, high = pi)

        if random_radius:
            radius_list = np.random.uniform(low = 0.2, high = 1, size = (num,))
        else:
            radius_list = [radius for i in range(num)]

        return state_list, goal_list, radius_list
    
    def random_start_goal(self, interval = 1, square=[0, 0, 10, 10], **kwargs):

        num = self.robot_num
        random_list = []
        goal_list = []
        while len(random_list) < 2*num:

            new_point = np.random.uniform(low = square[0:2]+[-pi], high = square[2:4]+[pi], size = (1, 3)).T

            if not self.check_collision(new_point, random_list, self.obs_line_list, interval):
                random_list.append(new_point)

        start_list = random_list[0 : num]
        goal_temp_list = random_list[num : 2 * num]

        for goal in goal_temp_list:
            goal_list.append(np.delete(goal, 2, 0))

        return start_list, goal_list
    
    def random_goal(self, interval = 1, square=[0, 0, 10, 10], **kwargs):

        num = self.robot_num
        random_list = []
        goal_list = []
        while len(random_list) < num:

            new_point = np.random.uniform(low = square[0:2]+[-pi], high = square[2:4]+[pi], size = (1, 3)).T

            if not self.check_collision(new_point, random_list, self.obs_line_list, interval):
                random_list.append(new_point)

        goal_temp_list = random_list[:]

        for goal in goal_temp_list:
            goal_list.append(np.delete(goal, 2, 0))

        return goal_list

    def distance(self, point1, point2):
        diff = point2[0:2] - point1[0:2]
        return np.linalg.norm(diff)

    def check_collision(self, check_point, point_list, line_list, range):

        for point in point_list:
            if self.distance(check_point, point) < range:
                return True
            
            for segment in line_list:
                if self.seg_dis(segment, check_point) < range:
                    return True
        
        return False


    def step(self, vel_list=[], **vel_kwargs):

        # vel_kwargs: vel_type = 'diff', 'omni'
        #             stop=True, whether stop when arrive at the goal
        #             noise=False, 
        #             alpha = [0.01, 0, 0, 0.01, 0, 0], noise for diff
        #             control_std = [0.01, 0.01], noise for omni

        for robot, vel in zip(self.robot_list, vel_list):
            robot.move_forward(vel, **vel_kwargs)

    def cal_des_list(self):
        vel_list = list(map(lambda x: x.cal_des_vel() , self.robot_list))
        return vel_list
    
    def cal_des_omni_list(self):
        vel_list = list(map(lambda x: x.cal_des_vel_omni() , self.robot_list))
        return vel_list

    def arrive_all(self):

        for robot in self.robot_list:
            if not robot.arrive():
                return False

        return True

    def robots_reset(self, reset_mode=1, **kwargs):
        
        if reset_mode == 0:
            for robot in self.robot_list:
                robot.reset(self.random_bear)
        
        elif self.cur_mode != reset_mode:
            state_list, goal_list, _ = self.init_state_distribute(init_mode = reset_mode, **kwargs)

            for i in range(self.robot_num):
                self.robot_list[i].init_state = state_list[i]
                self.robot_list[i].goal = goal_list[i]
                self.robot_list[i].reset(self.random_bear) 
            
            self.cur_mode = reset_mode

        elif reset_mode == 2:
            state_list, goal_list = self.random_start_goal(**kwargs)
            for i in range(self.robot_num):
                self.robot_list[i].init_state = state_list[i]
                self.robot_list[i].goal = goal_list[i]
                self.robot_list[i].reset(self.random_bear) 
        
        elif reset_mode == 4:
            goal_list = self.random_goal(**kwargs)
            for i in range(self.robot_num):
                self.robot_list[i].goal = goal_list[i]
                self.robot_list[i].reset(self.random_bear)

        else:
            for robot in self.robot_list:
                robot.reset(self.random_bear)

    def robot_reset(self, id=0):
        self.robot_list[id].reset(self.random_bear)

    # states
    def total_states(self, env_train=True):
        
        robot_state_list = list(map(lambda r: np.squeeze( r.omni_state(env_train)), self.robot_list))
        nei_state_list = list(map(lambda r: np.squeeze( r.omni_obs_state(env_train)), self.robot_list))
        obs_circular_list = list(map(lambda o: np.squeeze( o.omni_obs_state(env_train) ), self.obs_cir_list))
        obs_line_list = self.obs_line_list
        
        return [robot_state_list, nei_state_list, obs_circular_list, obs_line_list]
        
    def render(self, time=0.1, save=False, path=None, i = 0, **kwargs):
        
        self.world_plot.draw_robot_diff_list(**kwargs)
        self.world_plot.draw_obs_cir_list()
        self.world_plot.pause(time)

        if save == True:
            self.world_plot.save_gif_figure(path, i)

        self.world_plot.com_cla()

    
    def seg_dis(self, segment, point):
        
        point = np.squeeze(point[0:2])
        sp = np.array(segment[0:2])
        ep = np.array(segment[2:4])

        l2 = (ep - sp) @ (ep - sp)

        if (l2 == 0.0):
            return np.linalg.norm(point - sp)

        t = max(0, min(1, ((point-sp) @ (ep-sp)) / l2 ))

        projection = sp + t * (ep-sp)

        distance = np.linalg.norm(point - projection) 

        return distance



#         float minimum_distance(vec2 v, vec2 w, vec2 p) {
#   // Return minimum distance between line segment vw and point p
#   const float l2 = length_squared(v, w);  // i.e. |w-v|^2 -  avoid a sqrt
#   if (l2 == 0.0) return distance(p, v);   // v == w case
#   // Consider the line extending the segment, parameterized as v + t (w - v).
#   // We find projection of point p onto the line. 
#   // It falls where t = [(p-v) . (w-v)] / |w-v|^2
#   // We clamp t from [0,1] to handle points outside the segment vw.
#   const float t = max(0, min(1, dot(p - v, w - v) / l2));
#   const vec2 projection = v + t * (w - v);  // Projection falls on the segment
#   return distance(p, projection);
# }