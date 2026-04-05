package src.main.nsb.project.controller;

import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import src.main.nsb.project.entity.OrderEntity;
import src.main.nsb.project.service.OrderService;

@RestController
@RequestMapping("/api/orders")
public class OrderController {

    private static final Logger logger = LoggerFactory.getLogger(OrderController.class);
    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @GetMapping
    public List<OrderEntity> getAll() {
        logger.info("Get all orders");
        return orderService.findAll();
    }

    @GetMapping("/{orderId}")
    public ResponseEntity<OrderEntity> getById(@PathVariable Integer orderId) {
        logger.info("Get order by id: {}", orderId);
        return orderService.findById(orderId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<OrderEntity> create(@RequestBody OrderEntity order) {
        logger.info("Create order");
        return ResponseEntity.ok(orderService.create(order));
    }

    @PutMapping("/{orderId}")
    public ResponseEntity<OrderEntity> update(@PathVariable Integer orderId, @RequestBody OrderEntity order) {
        logger.info("Update order: {}", orderId);
        order.setOrderId(orderId);
        return ResponseEntity.ok(orderService.update(order));
    }

    @DeleteMapping("/{orderId}")
    public ResponseEntity<Void> delete(@PathVariable Integer orderId) {
        logger.info("Delete order: {}", orderId);
        orderService.delete(orderId);
        return ResponseEntity.noContent().build();
    }
}