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

def perspective_fov(fov, aspect_ratio, near_plane, far_plane):
    num = 1.0 / np.tan(fov / 2.0)
    num9 = num / aspect_ratio
    return np.array([
        [num9, 0.0, 0.0, 0.0],
        [0.0, num, 0.0, 0.0],
        [0.0, 0.0, far_plane / (near_plane - far_plane), -1.0],
        [0.0, 0.0, (near_plane * far_plane) / (near_plane - far_plane), 0.0]
    ])

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
    rot_matrix = np.array([[r00, r01, r02, 0],
                           [r10, r11, r12, 0],
                           [r20, r21, r22, 0],
                           [0, 0, 0, 1]])
                            
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
        mat = quaternion_rotation_matrix(self.__rotation)
        vertices = np.pad(self.__vertices, ((0,0),(0,1)), mode='constant', constant_values=0)
        location = vertices.dot(mat)  # an index->location mapping
        pos_pad = np.pad(self.__pos, ((0),(1)), mode='constant', constant_values=0)
        location = np.add(location, pos_pad)
        location = location.dot(perspective_fov(90.0, 1.0, 0.01, 10.0))
        return ((location[v1][:3], location[v2][:3]) for v1, v2 in self.__edges)


######################
#                    #
#    gui section     #
#                    #
######################


BLACK, RED, GREEN, BLUE = (0, 0, 0), (255, 128, 128), (128, 255, 128), (128, 128, 255)



class Paint:
    def __init__(self, shapes, dongle):
        self.__shapes = shapes
        self.__dongle = dongle
        self.__size = 1000, 1000
        self.__clock = pygame.time.Clock()
        self.__screen = pygame.display.set_mode(self.__size)

        self.font = pygame.font.SysFont('Comic Sans MS', 30)

        self.__number_surfaces = [None] * 5
        for i in range(0, 5):
            self.__number_surfaces[i] = self.font.render(str(i), False, (255, 255, 255))

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

    def __draw_shape(self, thickness=4):
        colors = [RED, GREEN, BLUE]

        for shape in self.__shapes:
            idx = 0
            for start, end in shape.lines:
                pygame.draw.line(self.__screen, colors[idx % 3], self.__fit(start), self.__fit(end), thickness)
                idx += 1

        for i in range(0, 5):
            for start, end in shape.lines:
                self.__screen.blit(self.__number_surfaces[i], self.__fit(start))
                break

    def __mainloop(self):
        global pose_quat, pose_pos
        while True:
            self.__handle_events()
            self.__screen.fill(BLACK)
            self.__draw_shape()
            pygame.display.flip()

            for i in range(0, 5):
                #print(self.__dongle.get_pos(i), self.__dongle.get_rot(i))
                self.__shapes[i].set_pos(self.__dongle.get_pos(i) * -10.0)
                self.__shapes[i].set_quat(self.__dongle.get_rot(i))
            self.__dongle.do_loop()

######################
#                    #
#     main start     #
#                    #
######################


def main():
    from pygame import K_q, K_w, K_a, K_s, K_z, K_x

    cubes = [None] * 5
    for i in range(0, 5):
        cubes[i] = Physical(  # 0         1            2   3
            vertices=((0,0,0), (1, 0, 0), (0, 1, 0), (0, 0, 1)),
            edges=({0, 1}, {0, 2}, {0, 3})
        )

    dongle = DongleHID()
    #dongle = TrackerHID()

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Control -   q,w : X    a,s : Y    z,x : Z')
    Paint(cubes, dongle)

if __name__ == '__main__':
    main()
