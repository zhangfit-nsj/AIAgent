package src.main.nsb.project.exception;

public class OrderProcessingException extends RuntimeException {
    public OrderProcessingException() { super(); }
    public OrderProcessingException(String message) { super(message); }
    public OrderProcessingException(String message, Throwable cause) { super(message, cause); }
    public OrderProcessingException(Throwable cause) { super(cause); }
}