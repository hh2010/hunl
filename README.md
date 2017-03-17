## Heads Up No Limit Poker Solver

The [Jupyter notebook](hunl.ipynb) in this repository largely represents
the code from Will Tipton's [Solving Poker with IPython video series](http://www.husng.com/content/will-tipton-hunl-video-pack-2-0).

However, I have begun editing the code to add additional features and also
make the solver more user friendly.  For example, this code was only intended
to run on Windows for Python 2, but now also works on Python 3 and MacOS.

This was accomplished by removing the Equity Array creator functionality.  There are a lot of improvements that need to be made to that part of the program, so for now you can only run the Equity Arrays on the boards that are in the [eqarray](./eqarray) folder.

I have also begun working on a GUI interface for the solver.  Simply type
``./main.py`` in order to run it.  So far the only functionality are Hand vs Range and
Range vs Range equity calculations.

There is a lot of work to do on this project.  I look forward to spending
more time on it.  Let me know if you have any questions or comments: [hasan.haq@gmail.com](hasan.haq@gmail.com)
