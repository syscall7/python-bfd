from odaweb.instdoc.instdoc import InstDoc
import sqlite3

class i386(InstDoc):

    def __init__(self, mnemonic):

        super(i386,self).__init__(mnemonic)

        db = 'odaweb/instdoc/instdoc.db'
        connection=sqlite3.connect(db)
        cursor=connection.cursor()
        cursor.execute('SELECT short,long FROM instdoc WHERE platform="i386" AND mnemonic=?', (self.mnemonic,))
        result = cursor.fetchone()
        if result:
            (self.short, self.long) = result


