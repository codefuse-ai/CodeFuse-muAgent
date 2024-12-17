package com.example.bank;

public class Person {
    private String name;
    private BankAccount account;

    public Person(String name) {
        this.name = name;
        this.account = new BankAccount(this);
    }

    public String getName() {
        return name;
    }

    public BankAccount getAccount() {
        return account;
    }

    public void deposit(double amount) {
        account.deposit(amount);
        System.out.println(name + " deposited " + amount + " to their account.");
    }

    public void withdraw(double amount) {
        if (account.withdraw(amount)) {
            System.out.println(name + " withdrew " + amount + " from their account.");
        } else {
            System.out.println(name + " does not have enough balance to withdraw " + amount + ".");
        }
    }
}
