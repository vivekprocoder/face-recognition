'''
@author: vivek
'''
import os

from color import Color
from pyimage import PyImage
from graph import Graph

class FaceDetector(object):
    '''
    classdocs
    '''

    def __init__(self, filename, block_size = 5,
                 min_component_size = 10, majority = 0.5):
        '''
        Constructor - keeps input image filename, image read from the file as a PyImage object, block size (in pixels),
        threshold to decide how many skin color pixels are required to declare a block as a skin-block
        and min number of blocks required for a component. The majority argument says what fraction of
        the block pixels must be skin/hair colored for the block to be a skin/hair block - the default value is
        0.5 (half).
        '''
        
        
        self.input_image = PyImage(filename)
        self.block_size = block_size
        self.threshold = block_size * block_size * majority
        self.component_length = min_component_size
        self.majority = majority

    def skin_green_limits(self, red):
        '''
        Return the limits of normalized green given the normalized red component as a tuple (min, max)
        '''
        return ((-0.776*red.norm_r*red.norm_r + 0.5601*red.norm_r + 0.18),
                (-1.376*red.norm_r*red.norm_r + 1.0743*red.norm_r + 0.2))


    def is_skin(self, pixel_color):
        '''
        Given the pixel color (as a Color object) return True if it represents the skin color
        Color is skin if hue in degrees is (> 240 or less than or equal to 20) and 
        green is in the green limits and it is not white
        '''
        
    
        if((pixel_color.red > 95) and (pixel_color.green > 40)
           and (pixel_color.blue > 20)
           and ((max(pixel_color.red, pixel_color.green, pixel_color.blue)-
            min(pixel_color.red, pixel_color.green, pixel_color.blue)) > 15 )
           and (pixel_color.red-pixel_color.green > 15)
           and (pixel_color.red > pixel_color.green)\
           and (pixel_color.red > pixel_color.blue)):
            return True
        


    def is_hair(self, pixel_color):
        '''
        Return True if the pixel color represents hair - it is if intensity < 80 and ((B-G)<15 or (B-R)<15 or
        hue is between 20 and 40)
        '''
        
        
        if (pixel_color.intensity < 80 
            and ((pixel_color.norm_b - pixel_color.norm_g < 15)
            or (pixel_color.norm_b - pixel_color.norm_r < 15)
            or pixel_color.hue() in range (20, 41))):
            
            return True

        return False 


    def is_skin_hair_block(self, block, block_type):
        '''
        Return true if the block (given by the argument 'block' which is the coordinate-tuple for the top-left corner)
        is a skin/hair-block - it is if a majority (as per the threshold attribute) of the pixels in the block are
        skin/hair colored. 'block_type' says whether we are testing for a skin block ('s') or a hair block ('h).
        '''
        
        
        block_check = 0
        
        pixelx = block[0]
        pixely = block[1]        
                
        for pixelx in range (pixelx, pixelx + self.block_size ):
            for pixely in range (pixely, pixely + self.block_size):
                
                if self.input_image.get_rgba(pixelx, pixely) == None:
                    continue
                                
                color_block = Color(self.input_image.get_rgba(pixelx, pixely))
                
                if (self.is_skin(color_block) and block_type == 's'):
                    block_check += 1
                elif (self.is_hair(color_block) and block_type == 'h'):
                    block_check += 1

        return block_check >= self.threshold
            

    def add_neighbour_blocks(self, block, graph):
        '''
        Given a block (given by the argument 'block' which is the coordinate-tuple for the top-left corner)
        and a graph (could be a hair or a skin graph), add edges from the current block to its neighbours
        on the image that are already nodes of the graph
        Check blocks to the left, top-left and top of the current block and if any of these blocks is in the
        graph (means the neighbour is also of the same type - skin or hair) add an edge from the current block
        to the neighbour.
        '''
        
        
        for direction in ((-self.block_size, 0),
                          (-self.block_size, -self.block_size),
                          (0, -self.block_size),
                          (self.block_size, -self.block_size)):
            
            if (graph.is_node((block[0] + direction[0],
                block[1] + direction[1]))):
                
                graph.add_directed_edge(block, (block[0] + direction[0],
                                        block[1] + direction[1]))			


    def make_block_graph(self):
        '''
        Return the skin and hair graphs - nodes are the skin/hair blocks respectively
        Initialize skin and hair graphs. For every block if it is a  skin(hair) block
        add edges to its neighbour skin(hair) blocks in the corresponding graph
        For this to work the blocks have to be traversed in the top->bottom, left->right order
        '''
        
        
        comparison = lambda x, y : (1 if (x[0] > y[0])
                     else (0 if x[0]==y[0] else -1))
        
        skin_graph = Graph(comparison)
        hair_graph = Graph(comparison)
        
        pixelx = 0
        pixely = 0
        
        while pixely <= (self.input_image.size()[1] - self.block_size):

            while pixelx <= (self.input_image.size()[0] - self.block_size):

                if self.is_skin_hair_block((pixelx, pixely), 's'):
                    skin_graph.add_node((pixelx, pixely))
                    self.add_neighbour_blocks((pixelx, pixely), skin_graph)
                elif self.is_skin_hair_block((pixelx, pixely), 'h'):
                    hair_graph.add_node((pixelx, pixely))
                    self.add_neighbour_blocks((pixelx, pixely), hair_graph)

                pixelx += self.block_size
            
            pixelx = 0
            pixely += self.block_size
        
        return skin_graph, hair_graph


    def find_bounding_box(self, component):
        '''
        Return the bounding box - a box is a pair of tuples - ((minx, miny), (maxx, maxy)) for the component
        Argument 'component' - is just the list of blocks in that component where each block is represented by the
        coordinates of its top-left pixel.
        '''
        
        pixelx_list = []
        pixely_list = []
        
        for nodes in component:
            pixelx_list.append(nodes[0])
            pixely_list.append(nodes[1])
            
        return (((min(pixelx_list), min(pixely_list)),
                 (max(pixelx_list), max(pixely_list))))			
    
    def inside(self, corners, box):
        '''
        Check if a given coordinate lies inside the given box
        '''
        #print corners
        
        for corner in corners:
            if ((corner[0] >= box[0][0] and corner[1] >= box[0][1])
			        and (corner[0] <= box[1][0] and corner[1] <= box[1][1])):
                
                return True
            
        return False
                    
                    
    def skin_hair_match(self, skin_box, hair_box):
        '''
        Return True if the skin-box and hair-box given are matching according to one of the pre-defined patterns
        '''
        
        corner = [(skin_box[0][0], skin_box[0][1]),
                  (skin_box[0][0], skin_box[1][1]),
                  (skin_box[1][0], skin_box[0][1]),
                  (skin_box[1][0], skin_box[1][1])]
        
        if (self.inside(corner, hair_box)):
            return True

        elif skin_box[0][1] == hair_box[1][1]:
            return True

        else:
            return False


    def detect_faces(self):
        '''
        Main method - to detect faces in the image that this class was initialized with
        Return list of face boxes - a box is a pair of tuples - ((minx, miny), (maxx, maxy))
        Algo: (i) Make block graph (ii) get the connected components of the graph (iii) filter the connected components
        (iv) find bounding box for each component (v) Look for matches between face and hair bounding boxes
        Return the list of face boxes that have matching hair boxes
        '''
        
        
        skin_graph, hair_graph = self.make_block_graph()
        
        skin_components = skin_graph.get_connected_components()
        hair_components = hair_graph.get_connected_components()
        
        filtered_skin = []
        filtered_hair = []
        
        for component in skin_components:
            if len(component) >= self.component_length:
                filtered_skin.append(component)

        for component in hair_components:
            if len(component) >= self.component_length:
                filtered_hair.append(component)
        
        bound_face = []
        bound_hair = []
        
        for block in filtered_skin:
            bound_face.append(self.find_bounding_box(block))
        
        for block in filtered_hair:
            bound_hair.append(self.find_bounding_box(block))
            
    
        del filtered_skin, filtered_hair

        face_box = []
        
        for component in bound_face:
            for match in bound_hair:
                
                if (self.skin_hair_match(component, match)
                    == True):                    
                    face_box.append(component)

        return face_box
    
    def mark_box(self, box, color):
        '''
        Mark the box (same as in the above methods) with a given color (given as a raw triple)
        This is just a one-pixel wide line showing the box.
        '''
                
        for pixelx in range(box[0][0], box[1][0]):
            self.input_image.set(pixelx, box[0][1], color)
        for pixelx in range(box[0][0], box[1][0]):
            self.input_image.set(pixelx, box[1][1], color)
        for pixely in range(box[0][1], box[1][1]):
            self.input_image.set(box[0][0], pixely, color)
        for pixely in range(box[0][1], box[1][1]):
            self.input_image.set(box[1][0], pixely, color)    
    
    def mark_faces(self, marked_file):
        '''
        Detect faces and mark each face detected -- mark the bounding box of each face in red
        and save the marked image in a new file
        '''
        
        
        face_box = self.detect_faces()
            
        for box in face_box:
            self.mark_box(box, (255, 0, 0))

        self.input_image.save(marked_file)

if __name__ == '__main__':
    detect_face_in = FaceDetector('faces-05.jpeg', 12, 11, 0.19)
    detect_face_in.mark_faces('faces-05-marked.jpeg')
    detect_face_in = FaceDetector('faces-04.jpeg', 6, 10, 0.5)
    detect_face_in.mark_faces('faces-04-marked.jpeg')
    detect_face_in = FaceDetector('faces-03.jpeg', 6, 12, 0.7)
    detect_face_in.mark_faces('faces-03-marked.jpeg')
    detect_face_in = FaceDetector('faces-02.jpeg', 12, 9, 0.2)
    detect_face_in.mark_faces('faces-02-marked.jpeg')
    detect_face_in = FaceDetector('faces-01.jpeg', 7, 10, 0.3)
    detect_face_in.mark_faces('faces-01-marked.jpeg', )
