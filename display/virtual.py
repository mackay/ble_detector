
import pygame

from display.scene import World


class PyGameScene(World):

    def __init__(self, pixel_count, width=1200, height=400):
        super(PyGameScene, self).__init__(pixel_count)
        self.height = height
        self.width = ( width / pixel_count ) * pixel_count

        pygame.init()

        self.window = (self.width, self.height)
        self.screen = pygame.display.set_mode(self.window)
        self.background = pygame.Surface(self.window)

    def __to_color(self, pixel):
        return (pixel.r, pixel.g, pixel.b, pixel.a)

    def update(self):
        super(PyGameScene, self).update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run_enable = False

    def render(self):
        super(PyGameScene, self).render()

        pixel_width = self.width / len(self.pixels)
        pixel_height = self.height

        for idx, pixel in enumerate(self.pixels):
            pygame.draw.rect( self.background,
                              self.__to_color(pixel),
                              ( idx*pixel_width, 0,
                                pixel_width, pixel_height) )

            # self.background.set_at((0, idx), self.__to_color(pixel))

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
