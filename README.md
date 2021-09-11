# Voxelator
The all new way to turn your boring vector meshes into the new fad in town; Voxels!

Notes:
I have not tested this on a rotated mesh. With further testing I may improve on this.
It is necessary for a uniform scale on the mesh that is to be voxelated. In otherwords make sure your x scale, y scale, and z scale are all the same. (dimensions may be non-uniform)

Installation:
To install simply go to the top tool bar in blender under edit> preferences > addons > install, then choose voxelator.py
Once you are done simply select a single object, then in 3d view mode go under object > voxelate

Options:
Resolution size: Affects how many cubes will fill the longest axis of the mesh (other axis will have an automated amount)
Warning: Resolution affects load times of voxelation dramatically.

Fill volume: Whether or not to fill the entire voxelated mesh with cubes.

Separate Cubes: Cubes Will not be attached by vertices, they will each be their own individual cube. It does what it says on the tin.

Example:

Here is a model courtesy of: https://opengameart.org/users/quandtum
![original](https://user-images.githubusercontent.com/69417194/132940305-3836760b-7f8b-4f28-8814-f539ed4889dc.png)

And then here it is after being voxelated with a resolution of 64.
![voxelated](https://user-images.githubusercontent.com/69417194/132940308-22e9dded-104a-412c-a608-e2ffee93f7a7.png)

And the wireframe showing off those sweet generated cubes and totally empty volume.
![wireframe_voxelated](https://user-images.githubusercontent.com/69417194/132940312-0fef1e3f-dea6-4630-a154-99388956ea0c.png)

