import sys, json, time, gi
gi.require_version('Gtk','3.0'); gi.require_version('WebKit2','4.1')
from gi.repository import Gtk, WebKit2, GLib
plan=json.load(open(sys.argv[1]))
W,H=plan.get('width',1440),plan.get('height',900)
win=Gtk.OffscreenWindow(); win.set_default_size(W,H)
ctx=WebKit2.WebContext.new_ephemeral()
view=WebKit2.WebView.new_with_context(ctx); view.set_size_request(W,H)
s=view.get_settings(); s.set_enable_javascript(True); s.set_enable_developer_extras(False)
view.set_zoom_level(plan.get('zoom',1.0))
win.add(view); win.show_all()
steps=plan['steps']; i=[0]; busy=[False]
def finish(ok,msg):
    print(('ok  ' if ok else 'ERR ')+msg, flush=True)
def snap_cb(v,res,path):
    try:
        surf=v.get_snapshot_finish(res); surf.write_to_png(path); finish(True,'shot '+path)
    except Exception as e: finish(False,'snap '+str(e))
    GLib.timeout_add(300,next_step)
def run_js(js,cb):
    def done(v,res):
        try: v.evaluate_javascript_finish(res)
        except Exception as e: print('js:',e,flush=True)
        cb()
    view.evaluate_javascript(js,-1,None,None,None,done)
def do_step():
    st=steps[i[0]]
    def after_load():
        def after_js():
            def take():
                view.get_snapshot(WebKit2.SnapshotRegion.FULL_DOCUMENT if st.get('full',True) else WebKit2.SnapshotRegion.VISIBLE, WebKit2.SnapshotOptions.NONE, None, snap_cb, st['out'])
                return False
            if st.get('out'): GLib.timeout_add(st.get('wait_after_js',800),take)
            else: GLib.timeout_add(st.get('wait_after_js',800),next_step)
            return False
        if st.get('js'): run_js(st['js'],after_js)
        else: after_js()
        return False
    def on_load(v,ev):
        if ev==WebKit2.LoadEvent.FINISHED and busy[0]:
            busy[0]=False; GLib.timeout_add(st.get('wait',1500),after_load)
    hid=view.connect('load-changed',on_load)
    busy[0]=True
    if st.get('url'): view.load_uri(st['url'])
    else:
        busy[0]=False; after_load()
    steps[i[0]]['_hid']=hid
def next_step():
    if '_hid' in steps[i[0]]: view.disconnect(steps[i[0]]['_hid'])
    i[0]+=1
    if i[0]>=len(steps): Gtk.main_quit(); return False
    do_step(); return False
do_step(); Gtk.main()
