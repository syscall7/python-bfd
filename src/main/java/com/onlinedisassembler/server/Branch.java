package com.onlinedisassembler.server;

import java.util.ArrayList;
import java.util.Collections;

import com.onlinedisassembler.types.*;

public class Branch implements Comparable {
	
	public final int srcAddr;
	public final int targetAddr;
	public final int startAddr;
	public final int stopAddr;
	public final int span;
	public final boolean branchDown;
	public boolean isTargetAddrValid;
	private Object tag;
	
	public Branch(Instruction instr)
	{
		srcAddr = instr.address;
		targetAddr = instr.targetAddr;
		branchDown = srcAddr <= targetAddr;
		startAddr = branchDown ? srcAddr : targetAddr;
		stopAddr = branchDown ? targetAddr : srcAddr;
		span = stopAddr - startAddr;
		tag = null;
		isTargetAddrValid = instr.isTargetAddrValid;
	}
	
	public boolean overlaps(Branch b)
	{
		boolean ret = false;
		
		if ((b.stopAddr >= startAddr) && (b.stopAddr <= stopAddr))
		{
			ret = true;
		}
		else if ((stopAddr >= b.startAddr) && (stopAddr <= b.stopAddr))
		{
			ret = true;
		}
		
		return ret;
	}
	
	public boolean isSibling(Branch b)
	{
		return this.targetAddr == b.targetAddr;
	}
	
	public boolean spans(int addr)
	{
		return ((addr >= startAddr) && (addr <= stopAddr));
	}
	
	public boolean isSource(int addr)
	{
		return (addr == srcAddr);
	}
	
	public boolean isTarget(int addr)
	{
		return (addr == targetAddr);
	}
	
	public void setTag(Object o)
	{
		tag = o;
	}
	
	public Object getTag()
	{
		return tag;
	}

	@Override
	public int compareTo(Object arg0) {
		
		Branch b = (Branch) arg0;
		
		if (this.span < b.span)
			return -1;
		else if (this.span > b.span)
			return 1;
		else
			return 0;
	}
	

}
