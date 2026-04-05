package src.main.nsa.project.controller;

import jakarta.persistence.*;
import jakarta.transaction.Transactional;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Repository;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.*;
import src.main.nsa.project.dto.OrderDto;
import src.main.nsa.project.entity.CustomerEntity;
import src.main.nsa.project.entity.OrderEntity;
import src.main.nsa.project.exception.OrderProcessException;
import src.main.nsa.project.repository.CustomerRepository;
import src.main.nsa.project.repository.OrderRepository;
import src.main.nsa.project.service.OrderProcService;

public class OrderProcController {

    private static final Logger log = LoggerFactory.getLogger(OrderProcController.class);

    private final OrderProcService orderProcService;

    public OrderProcController(OrderProcService orderProcService) {
        this.orderProcService = orderProcService;
    }

    @GetMapping("/process")
    public ResponseEntity<List<OrderDto>> processOrders() {
        log.info("API called: /api/orders/process");
        List<OrderDto> result = orderProcService.mainProcess();
        return new ResponseEntity<>(result, HttpStatus.OK);
    }
}