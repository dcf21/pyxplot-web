#!/usr/bin/python2.4
# -*- coding: latin-1 -*-

import os, sys, codecs, string, glob, re
sys.path.append("/home/rpc25/plastex/lib/python2.4/site-packages")
from plasTeX.Renderers import Renderer

class Renderer(Renderer):

    def default(self, node):
        """ Rendering method for all non-text nodes """
        s = []

        # Handle characters like \&, \$, \%, etc.
        if len(node.nodeName) == 1 and node.nodeName not in string.letters:
            return self.textDefault(node.nodeName)

        # Start tag
        s.append('<%s>' % node.nodeName)

        # We don't want to do this
        # See if we have any attributes to render
        #if node.hasAttributes():
            #s.append('<attributes>')
            #for key, value in node.attributes.items():
                ## If the key is 'self', don't render it
                ## these nodes are the same as the child nodes
                #if key == 'self':
                    #continue
                #s.append('<%s>%s</%s>' % (key, unicode(value), key))
            #s.append('</attributes>')

        # Invoke rendering on child nodes
        s.append(unicode(node))

        # End tag
        s.append('</%s>' % node.nodeName)

        return u'\n'.join(s)

    def textDefault(self, node):
        """ Rendering method for all text nodes """
        text = unicode(node)
        # foo = re.match(u'‘', text)
        text2 = text.encode('ascii', 'xmlcharrefreplace')
        text2 = text2.replace('&#8217;', "'").replace('&#8216;', "`")
        text2 = text2.replace('&#8211;', "-").replace('&#960;', "pi")
        if (text != text2): print text2
        # if (foo == None): print text
        newnode = text2.replace(u'‘', 'badger')
        return newnode.replace('&','&amp;').replace('<','\\lab').replace('>','\\rab')

