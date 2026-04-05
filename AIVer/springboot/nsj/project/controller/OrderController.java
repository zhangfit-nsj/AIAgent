package nsj.project.controller;

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

public class OrderController {
    private static final Logger logger = LoggerFactory.getLogger(OrderController.class);

    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @GetMapping
    public List<OrderDto> getAllOrders() {
        logger.info("API: getAllOrders");
        return orderService.getAllOrders();
    }

    @GetMapping("/{id}")
    public OrderDto getOrderById(@PathVariable("id") Long id) {
        logger.info("API: getOrderById {}", id);
        return orderService.getOrderById(id);
    }

    @PostMapping
    public void createOrder(@RequestBody OrderDto dto) {
        logger.info("API: createOrder {}", dto);
        orderService.createOrder(dto);
    }

    @PutMapping("/{id}")
    public void updateOrder(@PathVariable("id") Long id, @RequestBody OrderDto dto) {
        logger.info("API: updateOrder {} {}", id, dto);
        dto.setOrId(id);
        orderService.updateOrder(dto);
    }

    @DeleteMapping("/{id}")
    public void deleteOrder(@PathVariable("id") Long id) {
        logger.info("API: deleteOrder {}", id);
        orderService.deleteOrder(id);
    }
}