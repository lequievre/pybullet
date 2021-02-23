#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laurent LEQUIEVRE
Research Engineer, CNRS (France)
Institut Pascal UMR6602
laurent.lequievre@uca.fr

forked from :

Copyright (C) 2019 Istituto Italiano di Tecnologia (IIT)
This software may be modified and distributed under the terms of the
LGPL-2.1+ license.

"""

import pybullet as p
from gym.utils import seeding

import pybullet_data

import numpy as np
import math as m

def get_objects_list():
    obj_list = [
        'duck_vhacd',
        'cube_small',
        'teddy_vhacd',
        'domino/domino',
    ]
    return obj_list

class WorldEnv:

    def __init__(self,
                 physicsClientId,
                 obj_name='duck_vhacd',
                 obj_pose_rnd_std=0.05,
                 workspace_lim=None):

        if workspace_lim is None:
            workspace_lim = [[0.25, 0.52], [-0.3, 0.3], [0.5, 1.0]]

        self._physics_client_id = physicsClientId
        self._ws_lim = tuple(workspace_lim)
        self._h_table = []
        self._obj_name = obj_name
        self._obj_pose_rnd_std = obj_pose_rnd_std
        self._obj_init_pose = []

        self.obj_id = None
        self.table_id = None

        # initialize
        self.seed()
        self.reset()

    def reset(self):

        # pybullet data path -> /home_directory/.local/lib/python3.8/site-packages/pybullet_data
        pybullet_data_path = pybullet_data.getDataPath()
        print("=> data path -> {0}".format(pybullet_data_path))

        # Add a search data path
        p.setAdditionalSearchPath(pybullet_data_path)
        # pybullet data path -> /home_directory/.local/lib/python3.8/site-packages/pybullet_data

        p.loadURDF("plane.urdf", [0, 0, 0], physicsClientId=self._physics_client_id)

        # Load table and object
        self.table_id = p.loadURDF("table/table.urdf",
                              basePosition=[0.85, 0.0, 0.0], useFixedBase=True, physicsClientId=self._physics_client_id)

        table_info = p.getCollisionShapeData(self.table_id, -1, physicsClientId=self._physics_client_id)[0]
        self._h_table = table_info[5][2] + table_info[3][2]/2

        # set ws limit on z according to table height
        self._ws_lim[2][:] = [self._h_table, self._h_table + 0.3]

        self.load_object(self._obj_name)


    def load_object(self, obj_name):

        # Load object. Randomize its start position if requested
        self._obj_name = obj_name
        self._obj_init_pose = self._sample_pose()
        self.obj_id = p.loadURDF(obj_name + ".urdf",
                                 basePosition=self._obj_init_pose[:3], baseOrientation=self._obj_init_pose[3:7],
                                 flags=p.URDF_USE_MATERIAL_COLORS_FROM_MTL,
                                 physicsClientId=self._physics_client_id)

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def _sample_pose(self):
        # ws_lim = self._ws_lim
        x_min = self._ws_lim[0][0] + 0.05
        x_max = self._ws_lim[0][1] - 0.1
        y_min = self._ws_lim[1][0] + 0.05
        y_max = self._ws_lim[1][1] - 0.05

        px = x_min + 0.5 * (x_max - x_min)
        py = y_min + 0.5 * (y_max - y_min)
        pz = self._h_table + 0.07

        quat = p.getQuaternionFromEuler([0.0, 0.0, 1/4*m.pi])

        if self._obj_pose_rnd_std > 0:
            # Add a Gaussian noise to position
            mu, sigma = 0, self._obj_pose_rnd_std
            # noise = self.np_random.normal(mu, sigma, 2)
            noise = [self.np_random.uniform(low=-self._obj_pose_rnd_std, high=self._obj_pose_rnd_std),
                     self.np_random.uniform(low=-self._obj_pose_rnd_std, high=self._obj_pose_rnd_std)]

            px = px + noise[0]
            py = py + noise[1]

            # Add uniform noise to yaw orientation
            quat = p.getQuaternionFromEuler([0, 0, self.np_random.uniform(low=-m.pi/4, high=m.pi/4)])

        px = np.clip(px, x_min, x_max)
        py = np.clip(py, y_min, y_max)

        obj_pose = (px, py, pz) + quat

        return obj_pose


    def debug_gui(self):
        size_line = 0.1
        p.addUserDebugLine([0, 0, 0], [size_line, 0, 0], [1, 0, 0], parentObjectUniqueId=self.obj_id, physicsClientId=self._physics_client_id)
        p.addUserDebugLine([0, 0, 0], [0, size_line, 0], [0, 1, 0], parentObjectUniqueId=self.obj_id, physicsClientId=self._physics_client_id)
        p.addUserDebugLine([0, 0, 0], [0, 0, size_line], [0, 0, 1], parentObjectUniqueId=self.obj_id, physicsClientId=self._physics_client_id)

