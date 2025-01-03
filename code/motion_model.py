'''
    Adapted from course 16831 (Statistical Techniques).
    Initially written by Paloma Sodhi (psodhi@cs.cmu.edu), 2018
    Updated by Wei Dong (weidong@andrew.cmu.edu), 2021
'''

import sys
import numpy as np
import math


class MotionModel:
    """
    References: Thrun, Sebastian, Wolfram Burgard, and Dieter Fox. Probabilistic robotics. MIT press, 2005.
    [Chapter 5]
    """
    def __init__(self, seed):
        """
        TODO : Tune Motion Model parameters here
        The original numbers are for reference but HAVE TO be tuned.
        """
        # For Reproducability
        np.random.seed(seed)
    

        # Keeping noise-low
        self._alpha1 = 0.00001
        self._alpha2 = 0.00001
        self._alpha3 = 0.0001
        self._alpha4 = 0.0001



    # Keep angle b/w [-pi pi]
    def angle_wrap(self, theta):
        return theta - 2*np.pi*np.floor((theta + np.pi)/(2*np.pi)) 


    def update_vectorized(self, u_t0, u_t1, X_t0):
        """
        param[in] u_t0 : particle state odometry reading [x, y, theta] at time (t-1) [odometry_frame]
        param[in] u_t1 : particle state odometry reading [x, y, theta] at time t [odometry_frame]
        param[in] X_t0 : particles state belief [p, x, y, theta] at time (t-1) [world_frame]
        param[out] X_t1 :particles state belief [p, x, y, theta] at time t [world_frame]
        """
        ###################################################
        #  Odom Motion Model-Probalistic Robotics(Ch5)  #  
        ###################################################
        # return X_t0
        if np.all(u_t0 == u_t1):
            return X_t0

        # Delta-change in Odometry 
        del_x, del_y, del_theta = u_t1 - u_t0
        
        del_rot_1 = np.arctan2(del_y, del_x) - u_t0[2]
        del_trans = np.sqrt(np.square(del_x) + np.square(del_y))
        del_rot_2 = del_theta - del_rot_1

        # Std-dev for Gaussian-Noise 
        std_rot1  = np.sqrt(self._alpha1*np.square(del_rot_1) + self._alpha2*np.square(del_trans))
        std_trans = np.sqrt(self._alpha3*np.square(del_trans) + self._alpha4*np.square(del_rot_1) + self._alpha4*np.square(del_rot_2)) 
        std_rot2  = np.sqrt(self._alpha1*np.square(del_rot_2) + self._alpha2*np.square(del_trans))

        # Overall Movement
        del_rot_1_bar = del_rot_1 - np.random.normal(0.0, std_rot1 ,  X_t0.shape[0])
        del_trans_bar = del_trans - np.random.normal(0.0, std_trans,  X_t0.shape[0])
        del_rot_2_bar = del_rot_2 - np.random.normal(0.0, std_rot2 ,  X_t0.shape[0])        

        
        # World-Frame Transformation
        X_t1 = np.array(X_t0) + np.array([
                                         del_trans_bar * np.cos(X_t0[:, 2] + del_rot_1_bar), 
                                         del_trans_bar * np.sin(X_t0[:, 2] + del_rot_1_bar),
                                         del_rot_1_bar + del_rot_2_bar
                                         ]).T
        
        X_t1[:, 2] = self.angle_wrap(X_t1[:, 2])
        
        return X_t1 


    def update(self, u_t0, u_t1, x_t0):
        """
        param[in] u_t0 : particle state odometry reading [x, y, theta] at time (t-1) [odometry_frame]
        param[in] u_t1 : particle state odometry reading [x, y, theta] at time t [odometry_frame]
        param[in] x_t0 : particle state belief [x, y, theta] at time (t-1) [world_frame]
        param[out] x_t1 : particle state belief [x, y, theta] at time t [world_frame]
        """
        """
        TODO : Add your code here
        """ 
        ###################################################
        #  Odom Motion Model-Probalistic Robotics(Ch5)  #  
        ###################################################

        if np.all(u_t0 == u_t1):
            return x_t0

        # Delta-change in Odometry 
        del_x, del_y, del_theta = u_t1 - u_t0
        
        del_rot_1 = np.arctan2(del_y, del_x) - u_t0[2]
        del_trans = np.sqrt(np.square(del_x) + np.square(del_y))
        del_rot_2 = del_theta - del_rot_1

        del_rot_1_bar = del_rot_1 - np.random.normal(
            loc=0.0, 
            scale=np.sqrt(
                self._alpha1*np.square(del_rot_1) + 
                self._alpha2*np.square(del_trans) 
                )
            )
        
        del_trans_bar = del_trans - np.random.normal(
            loc=0.0, 
            scale=np.sqrt(
                self._alpha3*np.square(del_trans) + 
                self._alpha4*np.square(del_rot_1) +
                self._alpha4*np.square(del_rot_2) 
            )
        )

        del_rot_2_bar = del_rot_2 - np.random.normal(
            loc=0.0,
            scale=np.sqrt(
                self._alpha1*np.square(del_rot_2) + 
                self._alpha2*np.square(del_trans)
            )
        )        

        x_t1 = np.zeros(3, dtype=np.float64)
        # World-Frame Transformation
        x_t1[0] = x_t0[0] + del_trans_bar*np.cos(x_t0[2] + del_rot_1_bar)
        x_t1[1] = x_t0[1] + del_trans_bar*np.sin(x_t0[2] + del_rot_1_bar)
        x_t1[2] = x_t0[2] + self.angle_wrap(del_rot_1_bar + del_rot_2_bar)

        return x_t1 

