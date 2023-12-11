from magicgui import magicgui
import datetime
import pathlib
import napari
from napari.layers import Image
import numpy as np


@magicgui(
    call_button="Calculate",
    slider_float={"widget_type": "FloatSlider", 'max': 10},
    dropdown={"choices": ['first', 'second', 'third']},
)
def widget_demo(
    maybe: bool,
    some_int: int,
    spin_float=3.14159,
    slider_float=4.5,
    string="Text goes here",
    dropdown='first',
    date=datetime.datetime.now(),
    filename=pathlib.Path('/some/path.ext')
):
    widget_demo.dropdown.choices = ['one']

#widget_demo.show()



@magicgui(call_button='Add Image')
def my_widget(ny: int=64, nx: int=64):
  return Image(np.random.rand(ny, nx), name='My Image')

viewer = napari.Viewer()
viewer.window.add_dock_widget(my_widget, area='right')
viewer.window.add_dock_widget(widget_demo, area='right')


my_widget()  # "call the widget" to call the function.

napari.run()