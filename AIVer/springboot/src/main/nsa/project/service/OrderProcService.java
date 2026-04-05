package src.main.nsa.project.service;

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

public class OrderProcService {

    private static final Logger log = LoggerFactory.getLogger(OrderProcService.class);

    private static final String VIP_TYPE = "VIP";
    private static final String END_FLAG_Y = "Y";

    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;

    public OrderProcService(OrderRepository orderRepository, CustomerRepository customerRepository) {
        this.orderRepository = orderRepository;
        this.customerRepository = customerRepository;
    }

    @Transactional
    public List<OrderDto> mainProcess() {
        log.info("Start mainProcess");
        List<OrderDto> resultList = new ArrayList<>();
        String wsEndFlag = "";
        int wsCount = 0;
        BigDecimal wsTotal = BigDecimal.ZERO;

        try {
            List<OrderEntity> orders = orderRepository.findAll();
            if (orders == null) {
                log.warn("Order list is null");
                throw new OrderProcessException("Order list is null");
            }
            for (OrderEntity order : orders) {
                if (order == null) {
                    log.warn("OrderEntity is null, skipping");
                    continue;
                }
                OrderDto dto = processOrder(order);
                if (dto != null) {
                    resultList.add(dto);
                    wsCount++;
                    wsTotal = wsTotal.add(dto.getOrAmount() != null ? dto.getOrAmount() : BigDecimal.ZERO);
                }
            }
            log.info("Processed {} orders, total amount={}", wsCount, wsTotal);
        } catch (Exception e) {
            log.error("Exception in mainProcess", e);
            throw new OrderProcessException("Error in mainProcess", e);
        }
        log.info("End mainProcess");
        return resultList;
    }

    private OrderDto processOrder(OrderEntity order) {
        if (order == null) {
            log.warn("processOrder: order is null");
            return null;
        }
        OrderDto dto = new OrderDto();
        dto.setOrId(order.getOrId());
        dto.setOrCustomerId(order.getOrCustomerId());
        dto.setOrAmount(order.getOrAmount());

        CustomerEntity customer = findCustomer(order.getOrCustomerId());
        if (customer != null) {
            dto.setCuName(customer.getCuName());
            dto.setCuType(customer.getCuType());
            dto.setVip(checkVip(customer));
        } else {
            dto.setCuName(null);
            dto.setCuType(null);
            dto.setVip(false);
        }
        return dto;
    }

    private CustomerEntity findCustomer(Long customerId) {
        if (customerId == null) {
            log.warn("findCustomer: customerId is null");
            return null;
        }
        Optional<CustomerEntity> opt = customerRepository.findByCuId(customerId);
        if (opt.isEmpty()) {
            log.warn("Customer not found: {}", customerId);
            return null;
        }
        return opt.get();
    }

    private boolean checkVip(CustomerEntity customer) {
        if (customer == null) {
            log.warn("checkVip: customer is null");
            return false;
        }
        return VIP_TYPE.equals(customer.getCuType());
    }
}