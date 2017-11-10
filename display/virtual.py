
import pygame

from display.scene import World


class PyGameScene(World):

    def __init__(self, pixel_count, pixel_size=5):
        super(PyGameScene, self).__init__(pixel_count)
        self.pixel_size = pixel_size

        pygame.init()

        #### Create a canvas on which to display everything ####
        self.window = (self.pixel_size * pixel_count, self.pixel_size)
        self.screen = pygame.display.set_mode(self.window)
        #### Create a canvas on which to display everything ####

        #### Create a surface with the same size as the window ####
        self.background = pygame.Surface(self.window)
        #### Create a surface with the same size as the window ####

    def __to_color(self, pixel):
        return (pixel.r, pixel.g, pixel.b, pixel.a)

    def render(self):
        super(PyGameScene, self).render()

        for idx, pixel in enumerate(self.pixels):
            pygame.draw.rect( self.background,
                              self.__to_color(pixel),
                              ( idx*self.pixel_size, 0,
                                self.pixel_size, self.pixel_size) )

            # self.background.set_at((0, idx), self.__to_color(pixel))

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

    def run(self, world_frame_callback=None):
        done = False
        while not done:
            self.update()

            if world_frame_callback:
                world_frame_callback(self)

            self.render()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

        pygame.quit()
