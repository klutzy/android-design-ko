#-*- encoding: utf8 -*-
import os
import shutil
from lxml import html

def parse(text):
    h = html.fromstring(text)
    content = h.get_element_by_id('content')
    ret = u''
    for i in content:
        # NOTE html.tostring() actually changes something; for example, &nbsp; becomes &#160;. Well it should not be a problem.
        if any('content-header' in j or 'content-footer' in j for j in i.values()):
            continue
        ret += html.tostring(i, pretty_print=True)
    return ret.strip()

def convert_dir(src, dest, func):
    for root, dirs, files in os.walk(src):
        newroot = root.replace(src, dest) # not safe
        defroot = root.replace(src, '') # not safe either
        try:
            os.makedirs(newroot)
        except:
            pass
        for fn in files:
            filename = os.path.join(root, fn)
            newfilename = os.path.join(newroot, fn)
            fullfilename = os.path.join(defroot, fn)
            func(filename, newfilename, fullfilename)

# TODO move to some template file?
NAVTOP = u"""
<div class="layout-content-row content-header ">
  <div class="layout-content-col span-9">
    <h2>{title}</h2>
    
  </div>
  <div class="paging-links layout-content-col span-4" itemscope itemtype="http://schema.org/SiteNavigationElement">
    <a href="#" class="prev-page-link">이전</a>
    <a href="#" class="next-page-link">다음</a>
  </div>
</div>
""".strip()

NAVBOTTOM = u"""
<div class="layout-content-row content-footer" itemscope itemtype="http://schema.org/SiteNavigationElement">
  <div class="paging-links layout-content-col span-9">&nbsp;</div>
  <div class="paging-links layout-content-col span-4">
    <a href="#" class="prev-page-link">이전</a>
    <a href="#" class="next-page-link">다음</a>
  </div>
</div>
""".strip()

TITLES = {
u"get-started/principles.html": u"Design Principles",
u"patterns/actionbar.html": u"Action Bar",
u"patterns/index.html": u"Patterns",
u"style/typography.html": u"Typography",
u"patterns/compatibility.html": u"Backwards Compatibility",
u"building-blocks/grid-lists.html": u"Grid Lists",
u"patterns/new-4-0.html": u"New in Android 4.0",
u"style/devices-displays.html": u"Devices and Displays",
u"style/themes.html": u"Themes",
u"patterns/pure-android.html": u"Pure Android",
u"building-blocks/pickers.html": u"Pickers",
u"style/iconography.html": u"Iconography",
u"style/writing.html": u"Writing Style",
u"building-blocks/tabs.html": u"Tabs",
u"style/color.html": u"Color",
u"building-blocks/progress.html": u"Progress and Activity",
u"building-blocks/buttons.html": u"Buttons",
u"downloads/index.html": u"Downloads",
u"patterns/notifications.html": u"Notifications",
u"style/metrics-grids.html": u"Metrics and Grids",
u"building-blocks/text-fields.html": u"Text Fields",
u"index.html": u"",
u"get-started/creative-vision.html": u"Creative Vision",
u"style/index.html": u"Style",
u"style/touch-feedback.html": u"Touch Feedback",
u"get-started/ui-overview.html": u"UI Overview",
u"building-blocks/lists.html": u"Lists",
u"patterns/multi-pane-layouts.html": u"Multi-pane Layouts",
u"patterns/navigation.html": u"Navigation with Back and Up",
u"patterns/app-structure.html": u"Application Structure",
u"patterns/swipe-views.html": u"Swipe Views",
u"building-blocks/spinners.html": u"Spinners",
u"building-blocks/scrolling.html": u"Scrolling",
u"patterns/gestures.html": u"Gestures",
u"building-blocks/dialogs.html": u"Dialogs",
u"building-blocks/switches.html": u"Switches",
u"building-blocks/seek-bars.html": u"Seek Bars and Sliders",
u"patterns/selection.html": u"Selection",
u"building-blocks/index.html": u"Building Blocks",
}

def extract_titles(filename, newfilename, fullfilename):
    if filename.endswith('html'):
        text = file(filename).read()
        h = html.fromstring(text)
        title = h.head.find('title')
        title = title.text.strip()
        if ' - ' in title:
            title = title.split(' - ',1)[1]
        else:
            title = ''
        TITLES[fullfilename] = title

def extract(filename, newfilename, *_):
    if filename.endswith('html'):
        p = parse(file(filename).read())
        file(newfilename, 'w').write(p)
    else:
        shutil.copyfile(filename, newfilename)

template = file('template.html').read().decode('utf8')
siteroot = None # "http://root.of/main/page/"index.html
def make(filename, newfilename, fullfilename):
    if filename.endswith('html'):
        text = file(filename).read().decode('utf8')
        title = TITLES[fullfilename]
        if title: title = ' - '+title
        navtop = NAVTOP
        navbottom = NAVBOTTOM
        if filename.endswith('index.html') and not filename.endswith('downloads/index.html'):
            navtop = ''
            navbottom = ''
        else:
            navtop = navtop.format(title=TITLES[fullfilename])
        args = {
            u'content': text,
            u'title': title,
            u'siteroot': siteroot,
            u'navtop': navtop,
            u'navbottom': navbottom,
        }
        args.update(TITLES)
        newtext = template.format(**args)
        file(newfilename, 'w').write(newtext.encode('utf8'))
    else:
        shutil.copyfile(filename, newfilename)

SOURCE = 'html'
EXTRACTTO = 'contents'
COMPILETO = 'out'
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 1:
        print "needs siteroot"
        sys.exit(1)
    siteroot = sys.argv[1]
    if len(sys.argv) > 2:
        arg = sys.argv[2]
        if arg == 'extract':
            convert_dir(SOURCE, EXTRACTTO, extract)
        elif arg == 'title':
            TITLES = {}
            convert_dir(SOURCE, EXTRACTTO, extract_titles)
            print "TITLES = {"
            for k in TITLES.keys():
                print u'''u"{key}": u"{val}",'''.format(key=k, val=TITLES[k])
            print "}"
    else:
        convert_dir(EXTRACTTO, COMPILETO, make)
