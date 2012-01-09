package com.onlinedisassembler.repository;

import java.util.UUID;

import org.hibernate.Criteria;
import org.hibernate.criterion.Restrictions;

import com.onlinedisassembler.types.User;

public class UserRepository extends Repository<User, String> {

	public UserRepository() {
		super(User.class);
	}

	public User getUser(String username) {
		Criteria c = getSession().createCriteria(User.class);
		c.add(Restrictions.eq("username", username));
		User u = (User) c.list().get(0);
		return u; 
	}
	
	public User createOrGetByEmail(String email) { 
		User u = this.load("email", email);
		if (u==null) { 
			u = new User(email, UUID.randomUUID().toString() );
			u.setEmail(email);
			save(u); 
		}
		return u; 
	}
}
