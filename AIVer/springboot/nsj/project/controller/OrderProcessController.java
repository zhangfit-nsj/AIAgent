package nsj.project.controller;

import jakarta.persistence.*;
import jakarta.transaction.Transactional;
import java.math.BigDecimal;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import nsj.project.entity.CustomerEntity;
import nsj.project.entity.OrderEntity;
import nsj.project.exception.OrderProcessException;
import nsj.project.repository.CustomerRepository;
import nsj.project.repository.OrderRepository;
import nsj.project.service.OrderProcessService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.*;

public class OrderProcessController {

    private static final Logger log = LoggerFactory.getLogger(OrderProcessController.class);

    private final OrderProcessService orderProcessService;

    public OrderProcessController(OrderProcessService orderProcessService) {
        this.orderProcessService = orderProcessService;
    }

    @PostMapping("/execute")
    public void executeOrderProcess() {
        log.info("API called: /api/order-process/execute");
        try {
            orderProcessService.mainProcess();
        } catch (OrderProcessException e) {
            log.error("OrderProcessException occurred", e);
            throw e;
        } catch (Exception e) {
            log.error("Unexpected exception occurred", e);
            throw new OrderProcessException("Unexpected error", e);
        }
    }
}