Edger
==

Edger is edit-mode tool for easy manipulation of mesh that has edgeloops, it works by adding loops to vertex groups and "locks them on a line" allowing the mesh to behave like it has only one edge on some parts, while that edge is divided.

[youtube demo](https://www.youtube.com/watch?v=ToHbROhUrEc)
Features:
--
* lock edgeloop verts on the line they sit
* make vertices unselectable (part of edgeloop locking)
* create a duplicate of the mesh without edgeloops (keeps original) (edgeloops have to be closed, ie. start is connected with end)
* on edgeloop vertex click, automatically select nearest corner
* coloring of vertices and edges (edger groups to see what is added)

Issues:
--
* [critical] operators for adding geometry (like ctrl+R, probably some other) inject new vertices to vertex groups of their adjacents, workaround is to either create all edgeloops first while no groups exist to be injected into, or go by adjacent groups and remove newly added group verts. (working on this atm)
* deleting geometry not tested! Basically all you have to keep track of is that the vertex groups ((named "_edger_.X") have the correct (and one edgeloop only!) vertices.
* minor situations where things don't update on mesh change. Just tab out and back to edit-mode
* faces get wierd shadows when verts are moved and canceled, they correct on any valid move tho.

Technical:
--
Modal operator, works with bmesh. Stores edgeloops in vertex groups, makes a list of custom classes that contain each vertex, its two line ends and ratio to one of them. Sets target vert position on the line with stored ratio so when any of ends is moved the vertex moves with them. Deselects all verts from edger groups.

Hope you like it!
For any questions, bug reports or suggestions please contact me at **reslav.hollos@gmail.com**
