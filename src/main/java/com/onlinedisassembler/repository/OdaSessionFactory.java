package com.onlinedisassembler.repository;

import org.hibernate.SessionFactory;
import org.hibernate.cfg.Configuration;

import com.onlinedisassembler.types.DisassembledFile;
import com.onlinedisassembler.types.User;

public class OdaSessionFactory {

    private static final SessionFactory sessionFactory = buildSessionFactory();

    private static SessionFactory buildSessionFactory() {
        try {
            // Create the SessionFactory from hibernate.cfg.xml
            return new Configuration()
             	.configure()
             	.addAnnotatedClass(DisassembledFile.class)
             	.addAnnotatedClass(User.class)
             	.buildSessionFactory();
        }
        catch (Throwable ex) {
            // Make sure you log the exception, as it might be swallowed
            System.err.println("Initial SessionFactory creation failed." + ex);
            throw new ExceptionInInitializerError(ex);
        }
    }

    public static SessionFactory getSessionFactory() {
        return sessionFactory;
    }

}
