
import pygame

from display import Renderer


class PyGameRenderer(Renderer):

    def __init__(self, width=1200, height=400):
        super(PyGameRenderer, self).__init__()
        self.target_height = height
        self.target_width = width

        self.height = height
        self.width = width

    def setup(self, pixel_count, world):
        super(PyGameRenderer, self).setup(pixel_count, world)

        self.height = self.target_height
        self.width = ( self.target_width / pixel_count ) * pixel_count

        pygame.init()

        self.window = (self.width, self.height)
        self.screen = pygame.display.set_mode(self.window)
        self.background = pygame.Surface(self.window)

        #keep a reference to the world - pygame has feeback to process
        self.world = world

    def render_buffer(self, pixel_buffer):
        super(PyGameRenderer, self).render_buffer(pixel_buffer)

        self.__process_pygame_events()

        pixel_width = self.width / len(pixel_buffer)
        pixel_height = self.height

        for idx, pixel in enumerate(pixel_buffer):
            pygame.draw.rect( self.background,
                              self.__to_color(pixel),
                              ( idx*pixel_width, 0,
                                pixel_width, pixel_height) )

            # self.background.set_at((0, idx), self.__to_color(pixel))

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

    def __to_color(self, pixel):
        return (pixel.r, pixel.g, pixel.b, pixel.a)

    def __process_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run_enable = False
