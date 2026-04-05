package src.main.nsb.project.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import src.main.nsb.project.service.OrderProcService;

@RestController
@RequestMapping("/api/orders")
public class OrderProcController {

    private static final Logger logger = LoggerFactory.getLogger(OrderProcController.class);

    private final OrderProcService orderProcService;

    public OrderProcController(OrderProcService orderProcService) {
        this.orderProcService = orderProcService;
    }

    @PostMapping("/process")
    public ResponseEntity<String> processOrders() {
        logger.info("Received request to process orders");
        try {
            orderProcService.processOrders();
            return ResponseEntity.ok("Order processing completed successfully");
        } catch (Exception e) {
            logger.error("Order processing failed", e);
            return ResponseEntity.status(500).body("Order processing failed: " + e.getMessage());
        }
    }
}