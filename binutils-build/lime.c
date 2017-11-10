/* BFD back-end for Lime objects.
   Copyright 1995, 1996, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005,
   2006, 2007, 2009, 2011 Free Software Foundation, Inc.
   Written by Ian Lance Taylor of Cygnus Support <ian@cygnus.com>.

   This file is part of BFD, the Binary File Descriptor library.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston,
   MA 02110-1301, USA.  */


/* This is what Lime files look like:
  
    lime_hdr, data, lime_hdr, data, lime_hdr, data, ...

 */
#include "sysdep.h"
#include "bfd.h"
#include "libbfd.h"
#include "libiberty.h"
#include "safe-ctype.h"
#include "bfd_stdint.h"

#define LIME_VERSION  1
#define LIME_MAGIC  0x4c694d45

/* The Lime header */

struct lime_hdr {
    uint32_t magic;     /* Lime magic number */
    uint32_t version;   /* Header version */
    uint64_t start;     /* starting address */
    uint64_t end;       /* ending address */
    uint64_t reserved;  /* reserved for future */
};

/* Re-use some of the the ihex data structures */

struct ihex_data_list
{
  struct ihex_data_list *next;
  bfd_byte *data;
  bfd_vma where;
  bfd_size_type size;
};

/* The ihex tdata information.  */

struct ihex_data_struct
{
  struct ihex_data_list *head;
  struct ihex_data_list *tail;
};


/* Create a lime object.  */

static bfd_boolean
lime_mkobject (bfd *abfd)
{
  struct ihex_data_struct *tdata;

  tdata = (struct ihex_data_struct *) bfd_alloc (abfd, sizeof (* tdata));
  if (tdata == NULL)
    return FALSE;

  abfd->tdata.ihex_data = tdata;
  tdata->head = NULL;
  tdata->tail = NULL;
  return TRUE;
}

/* Report a problem in a Lime file.  */
static void
lime_bad_version (bfd *abfd, file_ptr pos, uint32_t bad_version)
{
  (*_bfd_error_handler)
	(_("%B:%d: bad version `0x%08x' in Lime file"),
	 abfd, (uint32_t) pos, bad_version);
      bfd_set_error (bfd_error_bad_value);
}

static void
lime_bad_magic (bfd *abfd, file_ptr pos, uint32_t bad_magic)
{
  (*_bfd_error_handler)
	(_("%B:%d: bad magic `0x%08x' in Lime file"),
	 abfd, (uint32_t) pos, bad_magic);
      bfd_set_error (bfd_error_bad_value);
}

/* Read a Lime file and turn it into sections.  We create a new
   section for each contiguous set of bytes.  */

static bfd_boolean
lime_scan (bfd *abfd)
{
  struct lime_hdr hdr;

  if (bfd_seek (abfd, (file_ptr) 0, SEEK_SET) != 0)
    goto error_return;

  abfd->start_address = 0;

  while (sizeof(hdr) == bfd_bread(&hdr, sizeof(hdr), abfd))
  {
		char secbuf[20];
		char *secname;
		bfd_size_type amt;
		flagword flags;
    asection *sec = NULL;

    if (LIME_VERSION != hdr.version)
    {
      lime_bad_version(abfd, bfd_tell(abfd), hdr.version);
      goto error_return; 
    }

    if (LIME_MAGIC != hdr.magic)
    {
      lime_bad_magic(abfd, bfd_tell(abfd), hdr.magic);
      goto error_return; 
    }

    /* create the section */
		sprintf (secbuf, ".sec%d", bfd_count_sections (abfd) + 1);
		amt = strlen (secbuf) + 1;
		secname = (char *) bfd_alloc (abfd, amt);
		if (secname == NULL)
		  goto error_return;

		strcpy (secname, secbuf);
		flags = SEC_HAS_CONTENTS | SEC_LOAD | SEC_ALLOC;
		sec = bfd_make_section_with_flags (abfd, secname, flags);
		if (sec == NULL)
		  goto error_return;

		sec->vma = hdr.start;
		sec->lma = hdr.start;
		sec->size = hdr.end - hdr.start + 1;
		sec->filepos = bfd_tell(abfd);

    /* skip over the data */
    if (bfd_seek (abfd, (file_ptr) sec->size, SEEK_CUR) != 0)
      goto error_return; 
  }

  return TRUE;

error_return:

  return FALSE;
}

/* Try to recognize the Lime file.  */

static const bfd_target *
lime_object_p (bfd *abfd)
{
  void * tdata_save;
  struct lime_hdr hdr;

  if (bfd_seek (abfd, (file_ptr) 0, SEEK_SET) != 0)
    return NULL;

  if (bfd_bread (&hdr, sizeof(hdr), abfd) != sizeof(hdr))
  {
    if (bfd_get_error () == bfd_error_file_truncated)
      bfd_set_error (bfd_error_wrong_format);
    return NULL;
  }

  if ( (LIME_VERSION != hdr.version) || (LIME_MAGIC != hdr.magic))
  {
    bfd_set_error (bfd_error_wrong_format);
    return NULL;
  }

  /* TODO: Check the rest of the file for the correct format */

  /* OK, it looks like it really is a Lime file.  */
  tdata_save = abfd->tdata.any;
  if (! lime_mkobject (abfd) || ! lime_scan (abfd))
  {
    if (abfd->tdata.any != tdata_save && abfd->tdata.any != NULL)
      bfd_release (abfd, abfd->tdata.any);

    abfd->tdata.any = tdata_save;
    return NULL;
  }

  return abfd->xvec;
}

/* Read the contents of a section in an Intel Hex file.  */

static bfd_boolean
lime_read_section (bfd *abfd, asection *section, bfd_byte *contents)
{
  if (bfd_seek (abfd, section->filepos, SEEK_SET) != 0)
    return FALSE;

  if (bfd_bread (contents, (bfd_size_type) section->size, abfd) != section->size)
  {
    (*_bfd_error_handler)
	  (_("%B: bad section length in lime_read_section"), abfd);
    bfd_set_error (bfd_error_bad_value);
    return FALSE;
  }

  return TRUE;
}

/* Get the contents of a section in a Lime Hex file.  */

static bfd_boolean
lime_get_section_contents (bfd *abfd,
			   asection *section,
			   void * location,
			   file_ptr offset,
			   bfd_size_type count)
{
  if (section->used_by_bfd == NULL)
  {
    section->used_by_bfd = bfd_alloc (abfd, section->size);
    if (section->used_by_bfd == NULL)
      return FALSE;

    if (! lime_read_section (abfd, section,
                             (bfd_byte *) section->used_by_bfd))
      return FALSE;
  }

  memcpy (location, (bfd_byte *) section->used_by_bfd + offset,
	  (size_t) count);

  return TRUE;
}

/* Set the contents of a section in an Intel Hex file.  */

static bfd_boolean
lime_set_section_contents (bfd *abfd,
			   asection *section,
			   const void * location,
			   file_ptr offset,
			   bfd_size_type count)
{
  struct ihex_data_list *n;
  bfd_byte *data;
  struct ihex_data_struct *tdata;

  if (count == 0
      || (section->flags & SEC_ALLOC) == 0
      || (section->flags & SEC_LOAD) == 0)
    return TRUE;

  n = (struct ihex_data_list *) bfd_alloc (abfd, sizeof (* n));
  if (n == NULL)
    return FALSE;

  data = (bfd_byte *) bfd_alloc (abfd, count);
  if (data == NULL)
    return FALSE;
  memcpy (data, location, (size_t) count);

  n->data = data;
  n->where = section->lma + offset;
  n->size = count;

  /* Sort the records by address.  Optimize for the common case of
     adding a record to the end of the list.  */
  tdata = abfd->tdata.ihex_data;
  if (tdata->tail != NULL
      && n->where >= tdata->tail->where)
  {
      tdata->tail->next = n;
      n->next = NULL;
      tdata->tail = n;
  }
  else
  {
    struct ihex_data_list **pp;

    for (pp = &tdata->head;
         *pp != NULL && (*pp)->where < n->where;
         pp = &(*pp)->next);

    n->next = *pp;
    *pp = n;
    if (n->next == NULL)
      tdata->tail = n;
  }

  return TRUE;
}

/* Write out a lime object file.  */

static bfd_boolean
lime_write_object_contents (bfd *abfd)
{
  struct ihex_data_list *l;

  for (l = abfd->tdata.ihex_data->head; l != NULL; l = l->next)
  {
    struct lime_hdr hdr;

    hdr.version = LIME_VERSION;
    hdr.magic = LIME_MAGIC;
    hdr.start = l->where;
    hdr.end = l->where + l->size - 1;
    hdr.reserved = 0;

    if (bfd_bwrite (&hdr, sizeof(hdr), abfd) != sizeof(hdr))
      return FALSE;

    if (bfd_bwrite (l->data, (bfd_size_type) l->size, abfd) != l->size)
      return FALSE;
  }

  return TRUE;
}

/* Set the architecture for the output file.  The architecture is
   irrelevant, so we ignore errors about unknown architectures.  */

static bfd_boolean
lime_set_arch_mach (bfd *abfd,
		    enum bfd_architecture arch,
		    unsigned long mach)
{
  if (! bfd_default_set_arch_mach (abfd, arch, mach))
  {
    if (arch != bfd_arch_unknown)
      return FALSE;
  }
  return TRUE;
}

/* Get the size of the headers, for the linker.  */

static int
lime_sizeof_headers (bfd *abfd ATTRIBUTE_UNUSED,
		     struct bfd_link_info *info ATTRIBUTE_UNUSED)
{
  return 0;
}

/* Some random definitions for the target vector.  */

#define	lime_close_and_cleanup                    _bfd_generic_close_and_cleanup
#define lime_bfd_free_cached_info                 _bfd_generic_bfd_free_cached_info
#define lime_new_section_hook                     _bfd_generic_new_section_hook
#define lime_get_section_contents_in_window       _bfd_generic_get_section_contents_in_window
#define lime_get_symtab_upper_bound               bfd_0l
#define lime_canonicalize_symtab                  ((long (*) (bfd *, asymbol **)) bfd_0l)
#define lime_make_empty_symbol                    _bfd_generic_make_empty_symbol
#define lime_print_symbol                         _bfd_nosymbols_print_symbol
#define lime_get_symbol_info                      _bfd_nosymbols_get_symbol_info
#define lime_bfd_is_target_special_symbol         ((bfd_boolean (*) (bfd *, asymbol *)) bfd_false)
#define lime_bfd_is_local_label_name              _bfd_nosymbols_bfd_is_local_label_name
#define lime_get_lineno                           _bfd_nosymbols_get_lineno
#define lime_find_nearest_line                    _bfd_nosymbols_find_nearest_line
#define lime_find_inliner_info                    _bfd_nosymbols_find_inliner_info
#define lime_bfd_make_debug_symbol                _bfd_nosymbols_bfd_make_debug_symbol
#define lime_read_minisymbols                     _bfd_nosymbols_read_minisymbols
#define lime_minisymbol_to_symbol                 _bfd_nosymbols_minisymbol_to_symbol
#define lime_bfd_get_relocated_section_contents   bfd_generic_get_relocated_section_contents
#define lime_bfd_relax_section                    bfd_generic_relax_section
#define lime_bfd_gc_sections                      bfd_generic_gc_sections
#define lime_bfd_lookup_section_flags             bfd_generic_lookup_section_flags
#define lime_bfd_merge_sections                   bfd_generic_merge_sections
#define lime_bfd_is_group_section                 bfd_generic_is_group_section
#define lime_bfd_discard_group                    bfd_generic_discard_group
#define lime_section_already_linked               _bfd_generic_section_already_linked
#define lime_bfd_define_common_symbol             bfd_generic_define_common_symbol
#define lime_bfd_link_hash_table_create           _bfd_generic_link_hash_table_create
#define lime_bfd_link_hash_table_free             _bfd_generic_link_hash_table_free
#define lime_bfd_link_add_symbols                 _bfd_generic_link_add_symbols
#define lime_bfd_link_just_syms                   _bfd_generic_link_just_syms
#define lime_bfd_copy_link_hash_symbol_type \
  _bfd_generic_copy_link_hash_symbol_type
#define lime_bfd_final_link                       _bfd_generic_final_link
#define lime_bfd_link_split_section               _bfd_generic_link_split_section

/* The Intel Hex target vector.  */

const bfd_target lime_vec =
{
  "lime",			/* Name.  */
  bfd_target_lime_flavour,
  BFD_ENDIAN_UNKNOWN,		/* Target byte order.  */
  BFD_ENDIAN_UNKNOWN,		/* Target headers byte order.  */
  0,				/* Object flags.  */
  (SEC_HAS_CONTENTS | SEC_ALLOC | SEC_LOAD),	/* Section flags.  */
  0,				/* Leading underscore.  */
  ' ',				/* AR_pad_char.  */
  16,				/* AR_max_namelen.  */
  0,				/* match priority.  */
  bfd_getb64, bfd_getb_signed_64, bfd_putb64,
  bfd_getb32, bfd_getb_signed_32, bfd_putb32,
  bfd_getb16, bfd_getb_signed_16, bfd_putb16,	/* Data.  */
  bfd_getb64, bfd_getb_signed_64, bfd_putb64,
  bfd_getb32, bfd_getb_signed_32, bfd_putb32,
  bfd_getb16, bfd_getb_signed_16, bfd_putb16,	/* Headers. */

  {
    _bfd_dummy_target,
    lime_object_p,		/* bfd_check_format.  */
    _bfd_dummy_target,
    _bfd_dummy_target,
  },
  {
    bfd_false,
    lime_mkobject,
    _bfd_generic_mkarchive,
    bfd_false,
  },
  {				/* bfd_write_contents.  */
    bfd_false,
    lime_write_object_contents,
    _bfd_write_archive_contents,
    bfd_false,
  },

  BFD_JUMP_TABLE_GENERIC (lime),
  BFD_JUMP_TABLE_COPY (_bfd_generic),
  BFD_JUMP_TABLE_CORE (_bfd_nocore),
  BFD_JUMP_TABLE_ARCHIVE (_bfd_noarchive),
  BFD_JUMP_TABLE_SYMBOLS (lime),
  BFD_JUMP_TABLE_RELOCS (_bfd_norelocs),
  BFD_JUMP_TABLE_WRITE (lime),
  BFD_JUMP_TABLE_LINK (lime),
  BFD_JUMP_TABLE_DYNAMIC (_bfd_nodynamic),

  NULL,

  NULL
};
