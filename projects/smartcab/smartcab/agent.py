import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import operator
from numpy.random import choice
import numpy as np

# p=os.getcwd()
# if p=='/home/yifan/playground/Udacity_MLND/projects/smartcab':
#     os.chdir(p+'/smartcab/')

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor
        self.current_trial = 0
        self.num_random_action=0
        self.num_Q_action=0
        self.decay_factor=0.0005
        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed


    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)
        
        ########### 
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0
        if testing:
            self.epsilon=0
            self.alpha=0
        else:
            self.current_trial+=1
            print('current trial is {}'.format(self.current_trial))
            if self.learning:
                if self.epsilon>=0:
                    self.epsilon=self.epsilon-0.05
                    # self.epsilon=self.decay_factor**self.current_trial
                    # self.epsilon=np.exp(-self.decay_factor*self.current_trial)
                    # self.epsilon=np.cos(self.decay_factor*self.current_trial)
                    if self.epsilon<0.000001: self.epsilon=0.0001
                    print('epsilon is {:.5}'.format(self.epsilon))
        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint: left, right or forward
        inputs = self.env.sense(self)           # Visual input - intersection light (red or green)
                                                # and traffic (oncoming, right and left)
        deadline = self.env.get_deadline(self)  # Remaining deadline

        ########### 
        ## TO DO ##
        ###########
        # Set 'state' as a tuple of relevant data for the agent        
        # state = None
        # state=(waypoint, inputs, deadline)
        state=(waypoint, inputs)
        # state=(waypoint)

        return state


    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """
        ########### 
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state
        state_str=str(state)
        maxQ = max(self.Q[state_str].iteritems(), key=operator.itemgetter(1))[0]
        return maxQ 


    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0
        state_str=str(state)
        if state_str not in self.Q:
            self.Q[state_str] = {}
            self.Q[state_str]['action_0'] = 0
            self.Q[state_str]['action_1'] = 0
            self.Q[state_str]['action_2'] = 0
            self.Q[state_str]['action_3'] = 0

        print('number of state is {}'.format(len(self.Q)))
        return


    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None

        ########### 
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        if not self.learning:
            action=self.valid_actions[random.randint(0,len(self.valid_actions)-1)]
            self.num_random_action+=1
            print('choose random action {}'.format(action))
        else:
        # When learning, choose a random action with 'epsilon' probability
        #   Otherwise, choose an action with the highest Q-value for the current state
            print('choose action based on epsilon probability')
            rand_val = [True, False]
            weights = [self.epsilon, 1 - self.epsilon]
            random_action=choice(rand_val, p=weights)
            # random_action=True
            if random_action:
                action=self.valid_actions[random.randint(0,len(self.valid_actions)-1)]
                self.num_random_action += 1
                print('choose random action is {}'.format(action))
                print(self.num_random_action, self.num_Q_action)
            else:
                action_id=int(self.get_maxQ(self.state)[-1])
                action=self.valid_actions[action_id]
                self.num_Q_action+=1
                print('choose action is {}'.format(action))
                print(self.num_Q_action, self.num_Q_action)
        return action


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards 
            when conducting learning. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
        state_str=str(state)

        act_id=0
        for act in self.valid_actions:
            if act == action:
                break
            else:
                act_id+=1
        print('giving reward {:.6} to action {} for current state'.format(reward, self.valid_actions[act_id]))

        action_str='action_'+str(act_id)
        self.Q[state_str][action_str]=(1-self.alpha)*self.Q[state_str][action_str]+self.alpha*reward

        return


    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

        return
        

def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment()
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent, learning=True, alpha=0.5)
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent,enforce_deadline=True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    # sim = Simulator(env, update_delay=2, log_metrics=True, display=True)
    sim = Simulator(env, update_delay=0.01, log_metrics=True, display=False, optimized=False)

    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(n_test=10, tolerance=0.05)

    return agent

if __name__ == '__main__':
    agent=run()
    print('number of trial runs is {}'.format(agent.current_trial))
    print('number of states is {}'.format(len(agent.Q)))
    print('number of random actions is {}'.format(agent.num_random_action))
    print('number of actions based on Q-value is {}'.format(agent.num_Q_action))
