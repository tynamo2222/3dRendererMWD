import numpy as np
from math import cos, sin, pi
import cv2
from time import sleep

class Point():
    def __init__(self, img, x, y, z, text=True, text_value=""):
        # Defining position in 3D space
        self.x=x
        self.y=y
        self.z=z

        self.img=img

        # text for debugging
        self.text_draw = text
        self.text_value = text_value

        # other 3d parameters
        self.x_angle=0
        self.y_angle=0
        self.z_angle=0

        self.offset = (200, 200)
        self.scale = 100

        self.project_point()

    def project_point(self):
        # rotation matrices
        rotation_z=np.matrix([
            [cos(self.z_angle), -sin(self.z_angle), 0],
            [sin(self.z_angle), cos(self.z_angle), 0],
            [0, 0, 1]
        ])
        rotation_x = np.matrix([
            [1, 0, 0],
            [0, cos(self.x_angle), -sin(self.x_angle)],
            [0, sin(self.x_angle), cos(self.x_angle)],
        ])
        rotation_y = np.matrix([
            [cos(self.y_angle), 0, sin(self.y_angle)],
            [0, 1, 0],
            [-sin(self.y_angle), 0, cos(self.y_angle)]
        ])

        # projection matrix
        projection_matrix=np.matrix([
            [1, 0, 0],
            [0, 1, 0],
            #[0, 0, 0]
        ])

        point_matrix = np.matrix([
            [self.x],
            [self.y],
            [self.z]
        ])

        # converting point from 3d to 2d
        self.rotated_point=np.dot(rotation_x, point_matrix)
        self.rotated_point = np.dot(rotation_y, self.rotated_point)
        self.rotated_point = np.dot(rotation_z, self.rotated_point)

        projected_point=np.dot(projection_matrix, self.rotated_point)

        self.projected_x = int(projected_point[0][0]*self.scale)+self.offset[0]
        self.projected_y = int(projected_point[1][0]*self.scale)+self.offset[1]

        #self.draw()

    def draw_text(self):
        # draws text for debugging
        if self.text_draw:
            position_x = "X: " + str(round(float(self.rotated_point[0][0]),2))
            position_y = "Y: " + str(round(float(self.rotated_point[1][0]),2))
            position_z = "Z: " + str(round(float(self.rotated_point[2][0]),2))

            #print(position_string)
            cv2.putText(self.img, position_x, (self.get_coords()[0]+5, self.get_coords()[1]-15), cv2.FONT_HERSHEY_PLAIN, 1, [0, 0, 255])
            cv2.putText(self.img, position_y, (self.get_coords()[0]+5, self.get_coords()[1]), cv2.FONT_HERSHEY_PLAIN, 1, [0, 255, 0])
            cv2.putText(self.img, position_z, (self.get_coords()[0]+5, self.get_coords()[1]+15), cv2.FONT_HERSHEY_PLAIN, 1, [255, 0, 0])
            #cv2.putText(self.img, self.text_value, (self.get_coords()[0]+5, self.get_coords()[1]), cv2.FONT_HERSHEY_PLAIN, 1, [0, 255, 0])

    def draw(self):
        # draws the point
        cv2.circle(self.img, (self.projected_x, self.projected_y), 3, [255, 255, 255], 3)
        self.draw_text()

    def get_coords(self):
        # returns coords in 2d space
        return [self.projected_x, self.projected_y]

    def get_depth(self):
        # gets depth (z)
        return float(self.rotated_point[2][0])

class Line():
    def __init__(self, img, point_1, point_2, color=[200, 200, 200]):
        # defining points
        self.p1=point_1
        self.p2=point_2

        self.img=img
        self.color=color

    def draw(self):
        cv2.line(self.img, self.p1.get_coords(), self.p2.get_coords(), self.color, 2)
        self.p1.draw()
        self.p2.draw()

    def get_depth(self):
        # getting depth as average depth of both points
        p1d = float(self.p1.rotated_point[2][0])
        p2d = float(self.p2.rotated_point[2][0])

        return (p1d+p2d)/2

class Face():
    def __init__(self, img, points, color=[0, 255, 255], text_img=None):
        # points its connected to
        self.points=points
        self.img=img
        self.text_img=text_img
        self.color=color

    def draw(self):
        # fills a polygon with the chosen color
        points = []
        for i in range (len(self.points)):
            points.append(self.points[i].get_coords())

        cv2.fillPoly(self.img, [np.array(points)], self.color)

    def get_depth(self):
        # very WIP depth calculations
        x=0
        y=0
        z=0

        for pt in self.points:
            x += pt.get_coords()[0]
            y += pt.get_coords()[1]
            z += pt.get_depth()

        x /= len(self.points)
        y /= len(self.points)
        z /= len(self.points)
        #print(x, y)

        cv2.putText(self.text_img, str(round(z, 2)), (int(x), int(y)), cv2.FONT_HERSHEY_PLAIN, 1, self.color)

        return z

def main():
    # defining image size
    img_x=400
    img_y=400

    # creating image and window
    img = np.zeros((img_x,img_y,3), dtype=np.uint8)
    window = ""

    # defining points
    cube_points = [
        #back
        Point(img, -1, -1, 1, text_value="0"),
        Point(img, 1, -1, 1, text_value="1"),
        Point(img, 1, 1, 1, text_value="2"),
        Point(img, -1, 1, 1, text_value="3"),
        #front
        Point(img, -1, -1, -1, text_value="4"),
        Point(img, 1, -1, -1, text_value="5"),
        Point(img, 1, 1, -1, text_value="6"),
        Point(img, -1, 1, -1, text_value="7"),
    ]

    # defining faces
    cube_faces = [
        #back
        Face(img, [cube_points[0], cube_points[1], cube_points[2], cube_points[3]], [200, 200, 0]),
        #front
        Face(img, [cube_points[4], cube_points[5], cube_points[6], cube_points[7]], [0, 200, 200]),
        #right
        Face(img, [cube_points[1], cube_points[2], cube_points[6], cube_points[5]], [200, 0, 200]),
        #left
        Face(img, [cube_points[0], cube_points[4], cube_points[7], cube_points[3]], [200, 100, 150]),
        #top
        Face(img, [cube_points[5], cube_points[4], cube_points[0], cube_points[1]], [200, 100, 100]),
        #bottom
        Face(img, [cube_points[3], cube_points[2], cube_points[6], cube_points[7]], [100, 100, 200]),

    ]

    # defining lines
    cube_lines = [
        Line(img, cube_points[0], cube_points[1]),
        Line(img, cube_points[1], cube_points[2]),
        Line(img, cube_points[2], cube_points[3]),
        Line(img, cube_points[3], cube_points[0]),

        Line(img, cube_points[4], cube_points[5]),
        Line(img, cube_points[5], cube_points[6]),
        Line(img, cube_points[6], cube_points[7]),
        Line(img, cube_points[7], cube_points[4]),

        Line(img, cube_points[0], cube_points[4]),
        Line(img, cube_points[1], cube_points[5]),
        Line(img, cube_points[2], cube_points[6]),
        Line(img, cube_points[3], cube_points[7]),
    ]


    # showing image
    while(True):
        # clear
        wire_frame = np.zeros((img_x, img_y, 3), dtype=np.uint8)
        faces = np.zeros((img_x, img_y, 3), dtype=np.uint8)
        face_text = np.zeros((img_x, img_y, 3), dtype=np.uint8)

        objs = []

        # points
        for point in cube_points:
            #moving around points each frame
            point.img=wire_frame
            point.x_angle+=pi/360
            point.y_angle+=pi/360
            point.z_angle+=pi/360
            point.scale=sin(point.z_angle)*100
            #point.scale = sin(point.x_angle)*100
            point.project_point()
            objs.append(point)

        # lines
        for line in cube_lines:
            objs.append(line)
            line.img=wire_frame
            #line.draw()

        #faces
        for face in cube_faces:
            objs.append(face)
            face.img=faces
            face.text_img = face_text

        # axis
        if True:
            objs.append(Line(img, Point(img, 0, 0, 0, False), Point(img, 1, 0, 0, False), [0, 0, 255]))
            objs.append(Line(img, Point(img, 0, 0, 0, False), Point(img, 0, 1, 0, False), [0, 255, 0]))
            objs.append(Line(img, Point(img, 0, 0, 0, False), Point(img, 0, 0, 1, False), [255, 0, 0]))


        # drawing objects based on depth
        for i in range (len(objs)):
            furthest=0
            for j in range (len(objs)):
                if objs[j].get_depth() > objs[furthest].get_depth():
                    furthest=j
            objs[furthest].draw()
            #print(objs[furthest])
            objs.remove(objs[furthest])

        # displaying
        np.concatenate((faces, wire_frame), axis=0)
        np.concatenate((face_text, np.zeros((img_x,img_y,3), dtype=np.uint8)), axis=0)
        cv2.imshow(window, np.concatenate((faces, wire_frame), axis=1))

        sleep(0.01)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()
