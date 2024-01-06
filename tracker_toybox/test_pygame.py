import pygame
from numpy import array
from math import cos, sin
import numpy as np

from tracker_toybox import *

######################
#                    #
#    math section    #
#                    #
######################

X, Y, Z = 0, 1, 2

def quaternion_rotation_matrix(Q):
    """
    Covert a quaternion into a full three-dimensional rotation matrix.
 
    Input
    :param Q: A 4 element array representing the quaternion (q0,q1,q2,q3) 
 
    Output
    :return: A 3x3 element matrix representing the full 3D rotation matrix. 
             This rotation matrix converts a point in the local reference 
             frame to a point in the global reference frame.
    """
    # Extract the values from Q
    q0 = Q[0]
    q1 = Q[1]
    q2 = Q[2]
    q3 = Q[3]
     
    # First row of the rotation matrix
    r00 = 2 * (q0 * q0 + q1 * q1) - 1
    r01 = 2 * (q1 * q2 - q0 * q3)
    r02 = 2 * (q1 * q3 + q0 * q2)
     
    # Second row of the rotation matrix
    r10 = 2 * (q1 * q2 + q0 * q3)
    r11 = 2 * (q0 * q0 + q2 * q2) - 1
    r12 = 2 * (q2 * q3 - q0 * q1)
     
    # Third row of the rotation matrix
    r20 = 2 * (q1 * q3 - q0 * q2)
    r21 = 2 * (q2 * q3 + q0 * q1)
    r22 = 2 * (q0 * q0 + q3 * q3) - 1
     
    # 3x3 rotation matrix
    rot_matrix = np.array([[r00, r01, r02],
                           [r10, r11, r12],
                           [r20, r21, r22]])
                            
    return rot_matrix

def rotation_matrix(α, β, γ):
    """
    rotation matrix of α, β, γ radians around x, y, z axes (respectively)
    """
    sα, cα = sin(α), cos(α)
    sβ, cβ = sin(β), cos(β)
    sγ, cγ = sin(γ), cos(γ)
    return (
        (cβ*cγ, -cβ*sγ, sβ),
        (cα*sγ + sα*sβ*cγ, cα*cγ - sγ*sα*sβ, -cβ*sα),
        (sγ*sα - cα*sβ*cγ, cα*sγ*sβ + sα*cγ, cα*cβ)
    )


class Physical:
    def __init__(self, vertices, edges):
        """
        a 3D object that can rotate around the three axes
        :param vertices: a tuple of points (each has 3 coordinates)
        :param edges: a tuple of pairs (each pair is a set containing 2 vertices' indexes)
        """
        self.__vertices = array(vertices)
        self.__edges = tuple(edges)
        self.__rotation = np.array([0, 0, 0, 1])  # radians around each axis
        self.__pos = np.array([0,0,0])

    def set_quat(self, q):
        self.__rotation = q

    def set_pos(self, p):
        self.__pos = p

    @property
    def lines(self):
        vertices_shift = np.add(self.__vertices, self.__pos)
        location = vertices_shift.dot(quaternion_rotation_matrix(self.__rotation))  # an index->location mapping
        return ((location[v1], location[v2]) for v1, v2 in self.__edges)


######################
#                    #
#    gui section     #
#                    #
######################


BLACK, RED = (0, 0, 0), (255, 128, 128)


class Paint:
    def __init__(self, shape, keys_handler):
        self.__shape = shape
        self.__keys_handler = keys_handler
        self.__size = 1000, 1000
        self.__clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode(self.__size)
        self.__mainloop()

    def __fit(self, vec):
        """
        ignore the z-element (creating a very cheap projection), and scale x, y to the coordinates of the screen
        """
        # notice that len(self.__size) is 2, hence zip(vec, self.__size) ignores the vector's last coordinate
        return [round(70 * coordinate + frame / 2) for coordinate, frame in zip(vec, self.__size)]

    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        self.__keys_handler(pygame.key.get_pressed())

    def __draw_shape(self, thickness=4):
        for start, end in self.__shape.lines:
            pygame.draw.line(self.__screen, RED, self.__fit(start), self.__fit(end), thickness)

    def __mainloop(self):
        global pose_quat, pose_pos
        while True:
            self.__handle_events()
            self.__screen.fill(BLACK)
            self.__draw_shape()
            pygame.display.flip()

            self.__shape.set_pos(dongle_get_pos() * -10.0)
            self.__shape.set_quat(dongle_get_rot())
            do_loop()

######################
#                    #
#     main start     #
#                    #
######################


def main():
    from pygame import K_q, K_w, K_a, K_s, K_z, K_x

    cube = Physical(  # 0         1            2            3           4            5            6            7
        vertices=((1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1), (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1)),
        edges=({0, 1}, {0, 2}, {2, 3}, {1, 3},
               {4, 5}, {4, 6}, {6, 7}, {5, 7},
               {0, 4}, {1, 5}, {2, 6}, {3, 7})
    )

    def keys_handler(keys):
        pass

    do_usb_init()

    pygame.init()
    pygame.display.set_caption('Control -   q,w : X    a,s : Y    z,x : Z')
    Paint(cube, keys_handler)

if __name__ == '__main__':
    main()
