###############################################################################
# Date: 13/12/22
# Author: Sebastian Porras
# Aims: This is an implementation of the IDx tree. Can be initialised from a
# JSON object and created.Currently based on output from a joint reconstruction
# Has very basic structures that allow most variables to be accessed or set.
# To do:
# 1) Make a method that can parse this information into a nwk file so that
# it could be read by other tree viewers.
# 2) Investigate about adding in Branchpoint objects that store particular
# info about what parents are and how far away they are etc.
#################################################################################

import numpy as np
import numpy.typing as npt


class BranchPoint(object):
    """Represents a branchpoint on a phylogenetic tree. Can contain
    information about the parents or children of that point and how
    long that branch point is.

    Future use -> can associate annotations with this branch point
    """

    def __init__(self, id: str, parent: int, dist: float,
                 children: npt.ArrayLike) -> None:
        """ Constructs instance of a branchpoint.

        Parameters:
            id(str): Sequence ID

            parent(int): Index of parent branchpoint

            dist(float): Distance to parent

            children(np.array): all children of branchpoint

            isLeaf(bool): Marker for extant sequence
        """

        self._id = id
        self._parent = parent
        self._dist = dist
        self._children = children

    def __str__(self) -> str:

        return (f"Name: {self._id}\n\
        Parent Index: {self._parent}\n\
        Distance To Parent {self._dist}\n\
        Children IDs: {self._children}")


class IdxTree(object):
    """Represents a condensed phylogenetic tree. Each branchpoint is assigned 
    an index allowing easy access of information via that index. 
    """

    def __init__(self, nBranches: int, branchpoints: npt.NDArray,
                 parents: npt.NDArray, children: npt.NDArray, indices: dict,
                 distances: npt.NDArray) -> None:
        """
        Parameters:
            nBranchs(int): number of branch points in the tree 

            branchpoints(Array): Contains BranchPoint objects  

            parents(Array): maps the index of the child to the index 
            of the parent 

            children(Array): maps the index of the parent to an array 
            containing the indexes the child/children 

            indices(dict): Maps the sequence ID to the index on the tree 

            distances(Array): Maps the branchpoint to the distance to its parent 
        """

        self._nBranches = nBranches
        self._branchpoints = branchpoints
        self._parents = parents
        self._children = children
        self._indices = indices
        self._distances = distances

    def __str__(self) -> str:
        return f"Number of branchpoints: {self._nBranches}\nParents: {self._parents}\nChildren: {self._children}\nIndices: {self._indices}\nDistances: {self._distances}"

    def getIndexOf(self, name: str) -> int:
        """Retrieves the branchpoint index based on the sequence ID 

        Parameters:
            name (str): sequence name

        Returns:
            int: index of branchpoint for that sequence

        """

        return self._indices[name]


def IdxTreeFromJSON(serial: dict) -> IdxTree:
    """Instantiates a IdxTree object from a Json file

    Parameters:
        json_file (os.PathLike): path to json file 

    Returns:
        IdxTree
    """

    # Some reconstructions do not require tree distances
    try:
        jdists = serial["Input"]["Tree"]["Distances"]
    except KeyError:
        jdists = None

    try:
        # refer to IdxTree for explanation of these datatypes
        nBranches = serial["Input"]["Tree"]["Branchpoints"]
        jlabels = serial["Input"]["Tree"]["Labels"]
        jparents = serial["Input"]["Tree"]["Parents"]
    except:
        raise RuntimeError("Invalid JSON format")

    parents = np.array([None for i in range(nBranches)])
    bpoints = np.array([None for i in range(nBranches)])
    children = np.array([None for i in range(nBranches)])
    distances = np.array([None for i in range(nBranches)])
    indices = dict()

    for i in range(nBranches):

        # index by child branch point index and map their parent index
        parents[i] = jparents[i]

        if jdists is not None:

            # using same index as branch point, map distances
            distances[i] = jdists[i]
        else:
            distances[i] = None
        # index by sequence id and map branch point index
        indices[jlabels[i]] = i

    # Next step is to record children of each parent
    for PIdx in range(nBranches):

        curr_children = []

        # reference parent array and check if it matches current parent index
        for CIdx in range(nBranches):

            if (parents[CIdx] == PIdx):
                curr_children.append(CIdx)

        # Leaves will have no children which is recorded accordingly
        if len(curr_children) == 0:
            ch_array = np.array(None, dtype=None)
        else:
            ch_array = np.array(curr_children, dtype=int)

        children[PIdx] = ch_array

    # branch points mirror information in the tree but is more specific
    for BIdx in range(nBranches):

        # future implementations of branch points will have annotations
        bp = BranchPoint(id=jlabels[BIdx], parent=parents[BIdx],
                         dist=distances[BIdx], children=children[BIdx])

        bpoints[BIdx] = bp

    return IdxTree(nBranches=nBranches, branchpoints=bpoints, parents=parents,
                   children=children, indices=indices, distances=distances)
