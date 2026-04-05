package nsj.project.service;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;
import nsj.project.dto.CustomerDto;
import nsj.project.dto.OrderDto;
import nsj.project.dto.UserDto;
import nsj.project.entity.CustomerEntity;
import nsj.project.entity.OrderEntity;
import nsj.project.entity.UserEntity;
import nsj.project.repository.CustomerRepository;
import nsj.project.repository.OrderRepository;
import nsj.project.repository.UserRepository;
import nsj.project.service.CustomerService;
import nsj.project.service.OrderService;
import nsj.project.service.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

public class OrderService {
    private static final Logger logger = LoggerFactory.getLogger(OrderService.class);

    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;

    public OrderService(OrderRepository orderRepository, CustomerRepository customerRepository) {
        this.orderRepository = orderRepository;
        this.customerRepository = customerRepository;
    }

    @Transactional(readOnly = true)
    public List<OrderDto> getAllOrders() {
        logger.info("Fetching all orders");
        List<OrderEntity> entities = orderRepository.selectAll();
        return entities.stream().map(this::toDto).collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public OrderDto getOrderById(Long orId) {
        logger.info("Fetching order by id: {}", orId);
        OrderEntity entity = orderRepository.selectById(orId);
        if (entity == null) {
            logger.warn("Order not found: {}", orId);
            throw new RuntimeException("Order not found");
        }
        return toDto(entity);
    }

    @Transactional
    public void createOrder(OrderDto dto) {
        logger.info("Creating order: {}", dto);
        OrderEntity entity = toEntity(dto);
        orderRepository.insert(entity);
    }

    @Transactional
    public void updateOrder(OrderDto dto) {
        logger.info("Updating order: {}", dto);
        OrderEntity entity = toEntity(dto);
        int updated = orderRepository.update(entity);
        if (updated == 0) {
            logger.warn("Order not found for update: {}", dto.getOrId());
            throw new RuntimeException("Order not found for update");
        }
    }

    @Transactional
    public void deleteOrder(Long orId) {
        logger.info("Deleting order: {}", orId);
        int deleted = orderRepository.delete(orId);
        if (deleted == 0) {
            logger.warn("Order not found for delete: {}", orId);
            throw new RuntimeException("Order not found for delete");
        }
    }

    private OrderDto toDto(OrderEntity entity) {
        OrderDto dto = new OrderDto();
        dto.setOrId(entity.getOrId());
        dto.setOrCustomerId(entity.getOrCustomerId());
        dto.setOrAmount(entity.getOrAmount());
        return dto;
    }

    private OrderEntity toEntity(OrderDto dto) {
        OrderEntity entity = new OrderEntity();
        entity.setOrId(dto.getOrId());
        entity.setOrCustomerId(dto.getOrCustomerId());
        entity.setOrAmount(dto.getOrAmount());
        return entity;
    }
}