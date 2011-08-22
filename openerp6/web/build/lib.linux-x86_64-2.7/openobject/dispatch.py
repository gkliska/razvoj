import cherrypy

from openobject import pooler

class Dispatcher(cherrypy.dispatch.Dispatcher):
    """ The custom OpenObject dispatcher, using the object pool for its
    dispatching.

    Because it needs session data (among other things) and session data is not
    available during dispatch, this dispatcher is actually used as a CherryPy
    tool, running after the session tool has been initialized but before the
    handler is called (so it can replace it)
    """
    def __call__(self, path_info=None):
        request = cherrypy.request
        if not isinstance(request.handler, cherrypy.NotFound):
            return

        if path_info is None:
            path_info = request.path_info

        # cherrypy performs a request on this to force staticfile's
        # configuration (will request default.html on every
        # staticfile path), ignore it as we don't have files called
        # 'default.html'
        if path_info.endswith('default.html'):
            return

        # If we don't set it to a `False` default, we're probably going to
        # throw *a lot* which we don't want.
        # TODO: fix loading so this crap isn't needed anymore
        request.loading_addons = False
        super(Dispatcher, self).__call__(path_info)

    def find_handler(self, path):
        request = cherrypy.request

        pool = request.pool = pooler.get_pool()

        names = [x for x in path.strip("/").split("/") if x] + ["index"]
        node = pool.get_controller("/openerp")
        trail = [["/", node]]

        curpath = ""

        for name in names:
            objname = name.replace(".", "_")
            curpath = "/".join((curpath, name))
            next = pool.get_controller(curpath)
            if next is not None:
                node = next
            else:
                node = getattr(node, objname, None)
            trail.append([curpath, node])

        # Try successive objects (reverse order)
        num_candidates = len(trail) - 1
        for i in xrange(num_candidates, -1, -1):
            curpath, candidate = trail[i]
            if candidate is None:
                continue

            # Try a "default" method on the current leaf.
            if hasattr(candidate, "default"):
                defhandler = candidate.default
                if getattr(defhandler, 'exposed', False):
                    request.is_index = path.endswith("/")
                    return defhandler, names[i:-1]

            # Try the current leaf.
            if getattr(candidate, 'exposed', False):
                if i == num_candidates:
                    # We found the extra ".index". Mark request so tools
                    # can redirect if path_info has no trailing slash.
                    request.is_index = True
                else:
                    # We're not at an 'index' handler. Mark request so tools
                    # can redirect if path_info has NO trailing slash.
                    # Note that this also includes handlers which take
                    # positional parameters (virtual paths).
                    request.is_index = False
                return candidate, names[i:-1]

        return None, []
