Edger
==

Edger is edit-mode tool that "locks vertices on a line" allowing the mesh to behave like it has only one edge on some parts, while that edge is divided. It eases manipulations of mesh that needs edgeloops for subdivision operators.

[youtube demo](https://www.youtube.com/watch?v=ToHbROhUrEc)
Features:
--
* lock vertices on a line they sit (also makes them unselectable)
* create a duplicate of the mesh without edgeloops (keeps original)
* on edgeloop vertex click, automatically select nearest corner
* coloring of vertices and edges (edger groups to see what is added)

Issues:
--
* minor situations where things don't update on mesh change. Just tab out and back to edit-mode
* faces get wierd shadows when verts are moved and canceled, they correct on any valid move, or on tab out n back.

Technical:
--
Modal operator, works with bmesh. Stores edgeloops in vertex groups, makes a list of custom classes that contain each vertex, its two line ends and ratio to one of them. Sets target vert position on the line with stored ratio so when any of ends is moved the vertex moves with them. Deselects all verts from edger groups.

Hope you like it!
For any questions, bug reports or suggestions please contact me at **reslav.hollos@gmail.com**
