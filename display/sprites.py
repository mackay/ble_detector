from display import DynamicSprite


class Point(DynamicSprite):

    def __init__(self, color, position):
        super(Point, self).__init__(position=position)
        self.color = color

    def render_to(self, pixel_buffer):
        super(Point, self).render_to(pixel_buffer)

        if self.is_in_buffer(pixel_buffer):
            pixel_buffer[self.position].blend(self.color)


class Splotch(DynamicSprite):

    @staticmethod
    def __alpha_adjust(rgba):
        red, green, blue, alpha = rgba
        alpha = alpha * 0.5
        return red, green, blue, alpha

    def __init__(self, color, position, radius, edge_alpha_factor=0.5):
        super(Splotch, self).__init__(position)
        self.color = color
        self.radius = radius
        self.edge_alpha_factor = edge_alpha_factor

    @property
    def _start_position(self):
        return self.position - self.radius

    @property
    def _end_position(self):
        return self.position + self.radius

    def is_in_buffer(self, pixel_buffer):
        return ( super(Splotch, self).is_in_buffer(pixel_buffer, position=self._start_position) or
                 super(Splotch, self).is_in_buffer(pixel_buffer, position=self._end_position) )

    def render_to(self, pixel_buffer):
        super(Splotch, self).render_to(pixel_buffer)

        for i in range(self._start_position, self._end_position + 1):
            if not super(Splotch, self).is_in_buffer(pixel_buffer, position=i):
                continue

            opacity = self.color.a_n
            if i == self._start_position or i == self._end_position:
                opacity = self.edge_alpha_factor * self.color.a_n

            pixel_buffer[i].blend(self.color, opacity=opacity)


class SolidEdgeSplotch(Splotch):

    def __init__(self, color, position, radius, edge_alpha_factor=0.5):
        super(SolidEdgeSplotch, self).__init__(color, position, radius, edge_alpha_factor=edge_alpha_factor)

    def render_to(self, pixel_buffer):
        super(Splotch, self).render_to(pixel_buffer)

        for i in range(self._start_position, self._end_position + 1):
            if not super(Splotch, self).is_in_buffer(pixel_buffer, position=i):
                continue

            opacity = self.edge_alpha_factor * self.color.a_n
            if i == self._start_position or i == self._end_position:
                opacity = self.color.a_n

            pixel_buffer[i].blend(self.color, opacity=opacity)
