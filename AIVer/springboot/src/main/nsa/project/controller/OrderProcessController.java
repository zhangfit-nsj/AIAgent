package src.main.nsa.project.controller;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;
import src.main.nsa.project.dto.OrderDto;
import src.main.nsa.project.entity.CustomerEntity;
import src.main.nsa.project.entity.OrderEntity;
import src.main.nsa.project.exception.OrderProcessException;
import src.main.nsa.project.repository.CustomerRepository;
import src.main.nsa.project.repository.OrderRepository;
import src.main.nsa.project.service.OrderProcessService;

public class OrderProcessController {

    private static final Logger log = LoggerFactory.getLogger(OrderProcessController.class);

    private final OrderProcessService orderProcessService;

    public OrderProcessController(OrderProcessService orderProcessService) {
        this.orderProcessService = orderProcessService;
    }

    @PostMapping("/orders/process")
    public void processOrders() {
        log.info("API called: /orders/process");
        orderProcessService.processAllOrders();
    }
}