from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.parcel import ParcelList, Parcel
from oda.libs.odb.bfd.disassembler import Disassembler
from oda.apps.odaweb.models import BinaryString

MAX_COLUMNS = 32

def BranchComparator(a, b):
    if (a.span < b.span):
        return -1
    elif (a.span > b.span):
        return 1
    else:
        return 0

BLANK = 0
VPASSTHRU = 1<<1
HPASSTHRU = 1<<2
UPPERJOIN = 1<<3
LOWERJOIN = 1<<4
ARROW = 1<<5
NOARROW = 1<<6

class BranchLineHtmlFormatter:
    
    
    def __init__(self, branches):

        self.maxColAssigned = 0
        self.lastColFlags = []
        self.html = ''

        self.branchArray = branches[:]
        for b in branches:
            if not b.isTargetAddrValid:
                self.branchArray.remove(b)

        # sort branches based on span (so short, inner branches appear in inner columns)
        self.branchArray.sort(BranchComparator)
        self.assignColumns()

        # initialize to BLANK entries
        self.lastColFlags = [BLANK]*(self.maxColAssigned+1)
    
    def assignColumns(self):
        for b in self.branchArray:

            # initialize assigned column to null
            b.setTag(None)
            
            # assign it a column
            self.setFreeColumn(b)
    
    def setFreeColumn(self, b):

        # list of columns used by overalapping branches
        columnsUsed = []
        
        # list of branches that share a target addr with this branch
        siblingBranches = []

        freeColumn = None
        
        # for all the other branches
        for c in self.branchArray:

            # skip ourself
            if b is c:
                continue
            
            # if the column has been allocated and the two branches overlap
            if (c.getTag() != None) and c.overlaps(b):

                # if they are siblings, we want to use this column if there are no other conflicts
                if b.isSibling(c):

                    freeColumn = c.getTag()
                    
                    # track sibling branches
                    siblingBranches.append(c)

                # else, we can't use this column, so add it to the used list
                else:
                    usedColumn = c.getTag()

                    if usedColumn not in columnsUsed:
                        columnsUsed.append(usedColumn)

        # if we already have been assigned a column and we have siblings
        if b.getTag() is not None and siblingBranches:

            # get unique list of siblings' columns
            sibCols = list(set([sib.getTag() for sib in siblingBranches]))

            # if they all agree with each other and with us, there's nothing to do
            if len(sibCols) == 1 and sibCols[0] == b.getTag():
                return

        # if we didn't find a sibling match or the sibling column is in the used list
        if ((freeColumn is None) or (freeColumn in columnsUsed)):

            # TODO: Limit the number of columns displayed?

            # assign to next column
            freeColumn = self.maxColAssigned+1

            # check if there are any free columns in the address range of the branch span
            for col in range(self.maxColAssigned+1):
                # if we found a free column
                if col not in columnsUsed:
                    freeColumn = col
                    break

            # must set tag before updating siblings
            b.setTag(freeColumn)

            # update all siblings
            for sib in siblingBranches:
                # recursively resolve column conflicts among siblings
                self.setFreeColumn(sib)
        
        self.maxColAssigned = max(self.maxColAssigned, freeColumn)
        b.setTag(freeColumn)

    def buildHtmlRow(self, colFlags, isTarget):

        htmlRow = ""
        
        if isTarget:
            # add arrow
            htmlRow = self.flagsToHtml(ARROW)
        else:
            # add noarrow
            htmlRow = self.flagsToHtml(NOARROW)

        for i in range(self.maxColAssigned+1):
            htmlRow = self.flagsToHtml(colFlags[i]) + htmlRow
        
        #htmlRow += "<br>"
        
        return htmlRow
    
    def buildHtmlLabelRow(self, colFlags):
    
        htmlRow = ""
        
        # add noarrow
        htmlRow = self.flagsToHtml(NOARROW)
                
        for i in range(self.maxColAssigned+1):
            htmlRow = self.flagsToHtmlLabel(colFlags[i]) + htmlRow
        
        #htmlRow += "<br>"
        
        return htmlRow
    
    def pushAddr(self, addr):

        isTarget = False
        
        upperJoinCols = []
        lowerJoinCols = []
        passThruCols = []
        
        # for all branches
        for b in self.branchArray:

            assignedCol = b.getTag()
            if b.spans(addr) and (assignedCol is not None):

                if b.isTarget(addr):
                    isTarget = True
                    
                    if b.srcAddr > addr:
                        lowerJoinCols.append(assignedCol)
                    # TODO: handle branch to self
                    else:
                        upperJoinCols.append(assignedCol)

                elif b.isSource(addr):

                    if b.targetAddr > addr:
                        lowerJoinCols.append(assignedCol)
                    # TODO: handle branch to self
                    else:
                        upperJoinCols.append(assignedCol)
                else:
                    passThruCols.append(assignedCol)
        
        # highest of either type of join
        maxJoinCol = 0
        
        if lowerJoinCols:
            maxJoinCol = max(lowerJoinCols)
        
        if upperJoinCols:
            maxJoinCol = max(maxJoinCol, max(upperJoinCols))
        
        # calc number of columns necessary
        numCols = maxJoinCol+1
        
        if passThruCols:
            numCols = max(maxJoinCol, max(passThruCols)) + 1
        
        # build column map    
        for i in range(self.maxColAssigned+1):

            flags = BLANK
            
            if i in lowerJoinCols:
                flags |= LOWERJOIN

            if i in upperJoinCols:
                flags |= UPPERJOIN
            
            if (i < maxJoinCol):
                flags |= HPASSTHRU

            if i in passThruCols:
                flags |= VPASSTHRU
            
            self.lastColFlags[i] = flags

        h = self.buildHtmlRow(self.lastColFlags, isTarget)
        self.html += h
        return h
    
    def pushLabel(self, lines=1):
        nopLine = self.buildHtmlLabelRow(self.lastColFlags)
        h = lines*nopLine
        self.html += h
        return h
    
    def finalizeHtml(self):
        return self.html
    
    def flagsToHtmlLabel(self, flags):
        # remove HPASSTHRU
        flags &= ~HPASSTHRU
        
        # remove upper joins
        flags &= ~UPPERJOIN
        
        # convert lower joins to VPASSTHRU
        if ((flags & LOWERJOIN) != 0):
            flags &= ~LOWERJOIN
            flags |= VPASSTHRU
        
        return self.flagsToHtml(flags)
    
    def flagsToHtml(self, flags):
        html = BLANK
        
        toHtml = {
            BLANK: "&#x2001;",
            ARROW: "&#x25B6;",
            NOARROW: "&nbsp;",
            VPASSTHRU: "&#x2503;",
            HPASSTHRU: "&#x2501;",
            UPPERJOIN: "&#x2517;",
            LOWERJOIN: "&#x250F;",
            
            VPASSTHRU|HPASSTHRU:                     "&#x254B;",
            UPPERJOIN|LOWERJOIN|HPASSTHRU:           "&#x254B;",
            VPASSTHRU|HPASSTHRU|UPPERJOIN:           "&#x254B;",
            VPASSTHRU|HPASSTHRU|LOWERJOIN:           "&#x254B;",
            VPASSTHRU|HPASSTHRU|UPPERJOIN|LOWERJOIN: "&#x254B;",
            
            VPASSTHRU|UPPERJOIN:            "&#x2523;",
            VPASSTHRU|LOWERJOIN:            "&#x2523;",
            UPPERJOIN|LOWERJOIN:            "&#x2523;",
            VPASSTHRU|UPPERJOIN|LOWERJOIN:  "&#x2523;",
                
            HPASSTHRU|UPPERJOIN: "&#x253B;",
            HPASSTHRU|LOWERJOIN: "&#x2533;",
        }

        if flags in toHtml:
            html = toHtml[flags]

        return html


class BranchGraphNode:
    def __init__(self, startAddr, endAddr, size, yesAddr, noAddr):
        self.startAddr = startAddr   # starting address of this block
        self.endAddr = endAddr       # location of the branch (i.e., the last instruction of this block)
        self.yesAddr = yesAddr       # location to branch to if branch is taken
        self.noAddr = noAddr         # location to branch to if branch is not taken (i.e., next instruction)
        self.size = size             # number of bytes in this block

    def split(self, vma, parcels):
        if (vma not in self) or (vma == self.startAddr):
            raise Exception("Invalid attempt to split a node")

        newSelfSize = vma - self.startAddr
        newNode = BranchGraphNode(vma, self.endAddr, self.size - newSelfSize, self.yesAddr, self.noAddr)
        self.endAddr = parcels.lda_to_vma(parcels.vma_to_lda(vma-1))
        self.yesAddr = vma
        self.noAddr = None
        self.size = newSelfSize

        return newNode

    def getId(self):
        return '0x%x' % self.startAddr
    id = property(getId)

    def __contains__(self, vma):
        return (vma >= self.startAddr) and (vma <= self.endAddr)

    def __repr__(self):
        no = '0x%08x' % self.noAddr if self.noAddr else 'None'
        yes = '0x%08x' % self.yesAddr if self.yesAddr else 'None'
        return "%s  0x%08x--0x%08x Yes:%s, No:%s %d bytes" % (self.__class__, self.startAddr, self.endAddr, yes, no, self.size)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


class BranchGraphView(list):

    def __init__(self, odb_file, vma):
        self.odb_file = odb_file
        start = None
        end = None
        self.parcels = ParcelList(odb_file.get_structure_list(Parcel))

        # first, some validation
        p = self.parcels.find_parcel_by_vma(vma)
        if p:
            # if this is not in a code section
            if not p.is_code:
                raise Exception("Graph view is not available for data sections!")
        # else, invalid address
        else:
            raise Exception("Graph view is not available for invalid address 0x%x!" % vma)

        if type(odb_file.binary) == BinaryString:
            # TODO: Handle nonzero base address
            start = 0
            end = odb_file.binary.size

        functions = sorted(odb_file.get_structure_list(Function), key=lambda f: f.offset)
        for f in functions:
            if vma >= f.offset:
                start = f.offset
            elif vma < f.offset:
                end = f.offset
                break

        # get all the branches within this function
        branches = filter(lambda b: b.srcAddr >= start and b.srcAddr < end,
                            odb_file.get_structure_list(Branch))

        # dict of nodes, keyed by starting address of the block
        self._nodes = {}
        thisBlock = start

        for b in sorted(branches, key=lambda b: b.srcAddr):
            # Older versions of ODB files did not store the 'size' attribute of a DisplayUnit in the
            # branch structure list, so we hack around that here instead of upgrading all the old ODB files.
            if not hasattr(b.instr, 'size'):
                line = self.parcels.vma_to_lda(b.srcAddr)
                no = self.parcels.lda_to_vma(line+1)
            else:
                # address if the branch is not taken (i.e., the addr of the next instruction)
                no = b.srcAddr + b.instr.size

            # address if the branch is taken
            yes = b.targetAddr

            # first node
            self._nodes[thisBlock] = BranchGraphNode(thisBlock, b.srcAddr, no - thisBlock, yes, no)

            # advance to next block
            thisBlock = b.srcAddr + b.instr.size

        # make last block
        if thisBlock != end:
            end_line = self.parcels.vma_to_lda(end-1)
            last_addr = self.parcels.lda_to_vma(end_line)
            self._nodes[thisBlock] = BranchGraphNode(thisBlock, last_addr, end - thisBlock, None, None)

        #
        # now break out any new blocks that are the targets of branches
        #
        newNodes = {}
        # for each node we've identified so far
        for key, node in self._nodes.iteritems():
            # we only have to check the 'yes' addresses
            addr = node.yesAddr
            if addr not in self._nodes and addr not in newNodes:
                for key2, parent in self._nodes.iteritems():
                    if addr in parent:
                        newNodes[addr] = parent.split(addr, self.parcels)

        self._nodes.update(newNodes)

    '''
    {
        nodes:
        [
            {id:X, instructions: [du1, du2, du3, du4 ... }
            {id:Y, instructions: [du9, du10, du11 .... }
            ....
        ]
        links: [
            { from:x, to:y, type: 'taken' }
            { from:y, to: z, type: 'notTaken'}
            { from:o, to: q, type: 'unconditional'}
        ]
    }
    '''
    def getNodes(self):

        dasm = Disassembler(self.odb_file)

        # convert _nodes to representation needed by front end
        nodes = []
        for startAddr, node in self._nodes.iteritems():
            startLine = self.parcels.vma_to_lda(startAddr)
            endLine = self.parcels.vma_to_lda(startAddr + node.size)
            if endLine is None:
                endLine = self.parcels.sum_ldas()
            dus = dasm.analyze(startAddr, endLine - startLine, False)
            nodes.append({'id': node.id, 'instructions': dus})

        return nodes

    def getLinks(self):
        links = []
        # convert _nodes to representation needed by front end
        for startAddr, node in self._nodes.iteritems():
            if node.noAddr:
                links.append({'from': node.id, 'to': self._nodes[node.noAddr].id, 'type': 'notTaken'})
                links.append({'from': node.id, 'to': self._nodes[node.yesAddr].id, 'type': 'taken'})
            elif node.yesAddr:
                links.append({'from': node.id, 'to': self._nodes[node.yesAddr].id, 'type': 'unconditional'})
            else:
                # else, this is the last node in the function, which has no links
                pass

        return links

    nodes = property(getNodes)
    links = property(getLinks)


