package src.main.nsb.project.service;

import java.util.List;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import src.main.nsb.project.entity.OrderEntity;
import src.main.nsb.project.exception.OrderProcessingException;
import src.main.nsb.project.repository.OrderRepository;

@Service
public class OrderService {
    private static final Logger logger = LoggerFactory.getLogger(OrderService.class);
    private final OrderRepository orderRepository;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    public List<OrderEntity> findAll() {
        logger.info("Fetching all orders");
        return orderRepository.findAll();
    }

    public Optional<OrderEntity> findById(Integer orderId) {
        logger.info("Fetching order by id: {}", orderId);
        return orderRepository.findByOrderId(orderId);
    }

    @Transactional
    public OrderEntity create(OrderEntity order) {
        logger.info("Creating order: {}", order.getOrderId());
        if (orderRepository.existsById(order.getOrderId())) {
            throw new OrderProcessingException("Order already exists: " + order.getOrderId());
        }
        return orderRepository.save(order);
    }

    @Transactional
    public OrderEntity update(OrderEntity order) {
        logger.info("Updating order: {}", order.getOrderId());
        if (!orderRepository.existsById(order.getOrderId())) {
            throw new OrderProcessingException("Order not found: " + order.getOrderId());
        }
        return orderRepository.save(order);
    }

    @Transactional
    public void delete(Integer orderId) {
        logger.info("Deleting order: {}", orderId);
        if (!orderRepository.existsById(orderId)) {
            throw new OrderProcessingException("Order not found: " + orderId);
        }
        orderRepository.deleteById(orderId);
    }
}