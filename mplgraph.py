#!/usr/bin/env python3

################################################################################
#
#   \file
#   \author     <a href="http://www.innomatic.ca">innomatic</a>
#   \brief      Matplotlib WxAgg backend embedded in wx.Panel
#

# Matplotlib requires wxPython 2.8+
# Set the wxPython version in lib\site-packages\wx.pth file
# or if you have wxversion installed then uncomment the lines below
#
#import wxversion
#wxversion.ensureMinimal('2.8')

from numpy import arange, sin, pi

import matplotlib

# WxAgg backend
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import wx

#--------1---------2---------3---------4---------5---------6---------7---------8
## matplotlib object on wx.Panel
#
# Create and expose matplotlib objects (figure, canvas, toolbar) on wx.Panel
#
class MplGraph(wx.Panel):

    def __init__(self, parent, hideToolbar=False):

        wx.Panel.__init__(self, parent)

        # mpl figure object
        self.figure = Figure()
        # mpl canvas object
        self.canvas = FigureCanvas(self, -1, self.figure)
        # mpl toolbar
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.ShowToolbar(not hideToolbar)
        self.SetSizer(self.sizer)
        self.Fit()

    ## show and hide matplotlib toolbar
    def ShowToolbar(self, flag):
        self.toolbar.Show(flag)
        self.Layout()

    ## Create a new axis
    def AddSubPlot(self, *args, **kwgs):
        # create axes object and return
        return self.figure.add_subplot(*args, **kwgs)

    ## return canvas object
    def GetCanvas(self):
        return self.canvas

    ## return figure object
    def GetFigure(self):
        return self.figure

    ## return matplotlib color map
    def GetColorMap(self):
        return matplotlib.cm

    ## realize axis
    def Draw(self):
        self.canvas.draw()

    ## clear axis
    def Clear(self):
        self.figure.clear()


#--------1---------2---------3---------4---------5---------6---------7---------8
if __name__=="__main__":

    import numpy as np

    class MyFrame(wx.Frame):

        def __init__(self, parent, title):
            wx.Frame.__init__(self, parent, title=title)

            # menu id
            self.idLine = wx.NewId()
            self.idHist = wx.NewId()
            self.idCont = wx.NewId()
            self.idShade = wx.NewId()
            # menu
            menu = wx.Menu()
            # menu item
            mitemLine = menu.Append(self.idLine, "Line", "")
            mitemHist = menu.Append(self.idHist, "Histogram", "")
            mitemCont = menu.Append(self.idCont, "Contour", "")
            mitemShade = menu.Append(self.idShade, "Shade", "")

            # menubar
            menubar = wx.MenuBar()
            menubar.Append(menu, "Demo")
            self.SetMenuBar(menubar)

            # panel
            self.pnlPlot = MplGraph(self)

            # event binding
            self.Bind(wx.EVT_MENU, self.OnDrawGraph, mitemLine)
            self.Bind(wx.EVT_MENU, self.OnDrawGraph, mitemHist)
            self.Bind(wx.EVT_MENU, self.OnDrawGraph, mitemCont)
            self.Bind(wx.EVT_MENU, self.OnDrawGraph, mitemShade)
            self.Bind(wx.EVT_CLOSE, self.OnClose)

            # sizer
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.sizer.Add(self.pnlPlot,1, wx.EXPAND)

            self.SetSizer(self.sizer)
            self.SetAutoLayout(1)
            self.sizer.Fit(self)
            self.Show()


        def OnDrawGraph(self, evt):

            # simple line plot
            if evt.GetId() == self.idLine:
                # clear previous plot
                self.pnlPlot.Clear()
                # acquire new axes
                ax = self.pnlPlot.AddSubPlot(111)

                x = np.linspace(0,10,500)
                dashes = [10,5,100,5]

                line1, = ax.plot(x, np.sin(x), '--', linewidth=2,
                        label='Dashes set retroactively')
                line1.set_dashes(dashes)

                line2, = ax.plot(x, -1 * np.sin(x), dashes=[30, 5, 10, 5],
                        label='Dashes set proactively')
                ax.legend(loc='lower right')

            # histogram
            elif evt.GetId() == self.idHist:
                # clear previous plot
                self.pnlPlot.Clear()
                # acquire new axes
                ax0 = self.pnlPlot.AddSubPlot(1,2,1)
                ax1 = self.pnlPlot.AddSubPlot(1,2,2)

                np.random.seed(0)
                mu = 200
                sigma = 25
                bins = [100, 150, 180, 195, 205, 220, 250, 300]
                x = np.random.normal(mu, sigma, size=100)

                ax0.hist(x, 20, normed=1, histtype='stepfilled', facecolor='g',
                        alpha=0.75)
                ax0.set_title('stepfilled')

                ax1.hist(x, bins, normed=1, histtype='bar', rwidth=0.8)
                ax1.set_title('unequal bins')

            # contour
            elif evt.GetId() == self.idCont:
                # clear previous plot
                self.pnlPlot.Clear()
                # acquire new axes
                ax = self.pnlPlot.AddSubPlot(111)
                # we need figure object
                fig = self.pnlPlot.GetFigure()

                Y,X = np.mgrid[-3:3:100j, -3:3:100j]
                U = -1 - X**2 + Y
                V = 1 + X - Y**2
                strm = ax.streamplot(X, Y, U, V, color=U, linewidth=2,
                        cmap=matplotlib.cm.autumn)
                fig.colorbar(strm.lines)

            elif evt.GetId() == self.idShade:
                # clear previous plot
                self.pnlPlot.Clear()
                # acquire new axes
                ax1 = self.pnlPlot.AddSubPlot(121)
                # we need figure object too
                fig = self.pnlPlot.GetFigure()

                # colormap
                cmap = matplotlib.cm.copper

                # import LightSource
                from matplotlib.colors import LightSource

                y,x = np.mgrid[-4:2:200j, -4:2:200j]
                z = 10 * np.cos(x**2 + y**2)
                ls = LightSource(315, 45)

                rgb = ls.shade(z, cmap)

                ax1.imshow(rgb, interpolation='bilinear')
                im = ax1.imshow(z, cmap=cmap)
                #im.remove()
                #fig.colorbar(im)
                ax1.set_title('shaded plot')

                # import Axes3D
                from mpl_toolkits.mplot3d import Axes3D
                ax2 = self.pnlPlot.AddSubPlot(122, projection='3d')

                X = np.arange(-5,5,0.25)
                Y = np.arange(-5,5,0.25)
                X,Y = np.meshgrid(X,Y)
                R = np.sqrt(X**2 + Y**2)
                Z = np.sin(R)
                
                #surface plot
                surf = ax2.plot_surface(X,Y,Z, cmap = matplotlib.cm.coolwarm,
                        linewidth=0, antialiased=False)
                
                ax2.set_title('3d surface plot')

            # draw plot
            self.pnlPlot.Draw()


        def OnClose(self, evt):
            # explicitly destroy the panel
            #self.pnlPlot.Close()
            # destroy self
            self.Destroy()


    app = wx.App()
    frame = MyFrame(None, "MplGraph demo")

    app.MainLoop()
