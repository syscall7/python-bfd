package com.onlinedisassembler.server;

import java.util.ArrayList;
import java.util.Collections;
import java.util.ListIterator;

public class BranchLineHtmlFormatter {
	
	private Branch[] branchArray = null;
	private final int BLANK = 0;
	private final int VPASSTHRU = 1<<1;
	private final int HPASSTHRU = 1<<2;
	private final int UPPERJOIN = 1<<3;
	private final int LOWERJOIN = 1<<4;
	private final int ARROW = 1<<5;
	private final int NOARROW = 1<<6;
	private int maxColAssigned = 0;
	private int[] lastColFlags;
	
	private String html;
	
	public BranchLineHtmlFormatter(ArrayList<Branch> branches)
	{
		ArrayList<Branch> validBranches = (ArrayList<Branch>)branches.clone();
		for (Branch b : branches)
		{
			if (!b.isTargetAddrValid)
				validBranches.remove(b);
		}
    	// sort branches based on span (so short, inner branches appear in inner columns)
    	Collections.sort(validBranches);
    	branchArray = new Branch[validBranches.size()];
    	validBranches.toArray(branchArray);
		this.assignColumns();
		this.lastColFlags = new int[maxColAssigned+1];
		this.html = "";
	}
	
	private void assignColumns()
	{    	    	
    	for (Branch b : branchArray)
    	{
    		// initialize assigned column to null
    		b.setTag(null);
    		
    		// assign it a column
    		setFreeColumn(b);
    	}
	}
	
	
	private void setFreeColumn(Branch b)
	{
		// list of columns used by overalapping branches
		ArrayList<Integer> columnsUsed = new ArrayList<Integer>();
		
		// list of branches that share a target addr with this branch
		ArrayList<Branch> siblingBranches = new ArrayList<Branch>();

		int freeColumn = -1;
		
		// for all the other branches
		for (Branch c : branchArray)
		{
			// skip ourself
			if (b.equals(c))
				continue;
			
			// if the column has been allocated and the two branches overlap
			if ((c.getTag() != null) && (c.overlaps(b)))
			{
				// if they are siblings, we want to use this column if there are no other conflicts
				if (b.isSibling(c))
				{
					freeColumn = (Integer) c.getTag();
					
					// track sibling branches
					siblingBranches.add(c);
				}
				// else, we can't use this column, so add it to the used list
				else
				{
					Integer usedColumn = (Integer)c.getTag();
					if (!columnsUsed.contains(usedColumn))
							columnsUsed.add(usedColumn);
				}
			}
		}
		
		// if we didn't find a sibling match or the sibling column is in the used list
		if ((freeColumn < 0) || columnsUsed.contains(freeColumn))
		{
			for (freeColumn = 0; freeColumn < columnsUsed.size(); freeColumn++)
			{
				// if we found a free column
				if (!columnsUsed.contains(freeColumn))
					break;
			}
			
			// update all siblings
		    ListIterator<Branch> litr = siblingBranches.listIterator();
		    while (litr.hasNext()) 
		    {
		      Branch sib = litr.next();
		      
		      // recursively resolve column conflicts among siblings
		      setFreeColumn(sib);
		    }
		}
		
		maxColAssigned = Math.max(maxColAssigned, freeColumn);
		b.setTag(freeColumn);
	}

	
	private String buildHtmlRow(int[] colFlags, boolean isTarget)
	{
		String htmlRow = "";
		
		if (isTarget)
		{
			// add arrow
			htmlRow = flagsToHtml(ARROW);
		}
		else
		{
			// add noarrow
			htmlRow = flagsToHtml(NOARROW);
		}
		
		for (int i = 0; i < maxColAssigned+1; i++)
			htmlRow = flagsToHtml(colFlags[i]) + htmlRow;
		
		htmlRow += "<br>";
		
		return htmlRow;
	}
	
	private String buildHtmlLabelRow(int[] colFlags)
	{
		String htmlRow = "";
		
		// add noarrow
		htmlRow = flagsToHtml(NOARROW);
				
		for (int i = 0; i < maxColAssigned+1; i++)
			htmlRow = flagsToHtmlLabel(colFlags[i]) + htmlRow;
		
		htmlRow += "<br>";
		
		return htmlRow;
	}
	
	public void pushAddr(int addr)
	{	
		boolean isTarget = false;
		
		ArrayList<Integer> upperJoinCols = new ArrayList<Integer>();
		ArrayList<Integer> lowerJoinCols = new ArrayList<Integer>();
		ArrayList<Integer> passThruCols = new ArrayList<Integer>();
		
		// for all branches
		for (Branch b : branchArray)
		{
			if (b.spans(addr))
			{
				int assignedCol = (Integer)b.getTag();
				if (b.isTarget(addr))
				{
					isTarget = true;
					
					if (b.srcAddr > addr)
						lowerJoinCols.add(assignedCol);
					// TODO: handle branch to self
					else
						upperJoinCols.add(assignedCol);
				}
				else if (b.isSource(addr))
				{					
					if (b.targetAddr > addr)
						lowerJoinCols.add(assignedCol);
					// TODO: handle branch to self
					else
						upperJoinCols.add(assignedCol);
				}
				else
				{
					passThruCols.add((Integer)b.getTag());
				}
			}
		}
		
		// highest of either type of join
		int maxJoinCol = 0;
		
		if (!lowerJoinCols.isEmpty())
			maxJoinCol = (Integer)Collections.max(lowerJoinCols);
		
		if (!upperJoinCols.isEmpty())
			maxJoinCol = Math.max(maxJoinCol, (Integer)Collections.max(upperJoinCols));
		
		// calc number of columns necessary
		int numCols = maxJoinCol+1;
		
		if (!passThruCols.isEmpty())
			numCols = Math.max(maxJoinCol, (Integer)Collections.max(passThruCols)) + 1;
		
		// build column map	
		for (int i = 0; i < maxColAssigned+1; i++)
		{
			int flags = BLANK;
			
			if (lowerJoinCols.contains(i))
				flags |= LOWERJOIN;

			if (upperJoinCols.contains(i))
				flags |= UPPERJOIN;
			
			if (i < maxJoinCol)
				flags |= HPASSTHRU;

			if (passThruCols.contains(i))
				flags |= VPASSTHRU;
			
			lastColFlags[i] = flags;
		}
		
		this.html += buildHtmlRow(lastColFlags, isTarget);
	}
	
	public void pushLabel()
	{
		this.html += buildHtmlLabelRow(lastColFlags);
	}
	
	public String finalizeHtml()
	{
		return this.html;
	}
	
	private String flagsToHtmlLabel(int flags)
	{
		// remove HPASSTHRU
		flags &= ~HPASSTHRU;
		
		// remove upper joins
		flags &= ~UPPERJOIN;
		
		// convert lower joins to VPASSTHRU
		if ((flags & LOWERJOIN) != 0)
		{
			flags &= ~LOWERJOIN;
			flags |= VPASSTHRU;
		}
		
		return flagsToHtml(flags);
	}
	
	private String flagsToHtml(int flags)
	{
		String s = "";
		
		switch (flags)
		{
			case BLANK:
				s = "&#x2001";
				break;
			case ARROW:
				s = "&#x25B6;";
				break;
			case NOARROW:
				s = "&nbsp;";
				break;
			case VPASSTHRU:
				s = "&#x2503;";
				break;
				
			case HPASSTHRU:
				s = "&#x2501;";
				break;
			
			case UPPERJOIN:
				s = "&#x2517;";
				break;
				
			case LOWERJOIN:
				s = "&#x250F;";
				break;
			
			case VPASSTHRU|HPASSTHRU:
			case VPASSTHRU|HPASSTHRU|UPPERJOIN:
			case VPASSTHRU|HPASSTHRU|UPPERJOIN|LOWERJOIN:
				s = "&#x254B;";
				break;
			
			case VPASSTHRU|UPPERJOIN:
			case VPASSTHRU|LOWERJOIN:
			case UPPERJOIN|LOWERJOIN:
			case VPASSTHRU|UPPERJOIN|LOWERJOIN:
				s = "&#x2523;";
				break;
				
			case HPASSTHRU|UPPERJOIN:
				s = "&#x253B;";
				break;
				
			case HPASSTHRU|LOWERJOIN:
				s = "&#x2533;";
				break;
		}
		
		return s;
	}
}
