
import pygame

from display.scene import World


class PyGameScene(World):

    def __init__(self, pixel_count, pixel_size=5):
        super(PyGameScene, self).__init__(pixel_count)
        self.pixel_size = pixel_size

        pygame.init()

        self.window = (self.pixel_size * pixel_count, self.pixel_size)
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

        for idx, pixel in enumerate(self.pixels):
            pygame.draw.rect( self.background,
                              self.__to_color(pixel),
                              ( idx*self.pixel_size, 0,
                                self.pixel_size, self.pixel_size) )

            # self.background.set_at((0, idx), self.__to_color(pixel))

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
