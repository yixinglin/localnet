package org.hsgt.controllers;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.hsgt.controllers.response.ControllerResponse;
import org.hsgt.entities.common.ShippingGroup;
import org.hsgt.services.ShippingGroupService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;

@Api(tags = "Shipment Management")
@RestController
@RequestMapping("/shipment/metro")
public class MetroShippingGroupController {

    @Qualifier("metroShippingGroupService")
    @Autowired
    ShippingGroupService shippingGroupService;


    @ApiOperation(value = "Get list of shipping groups", notes = "Get a list of shipping groups with group names and group IDs using Metro API.")
    @GetMapping("/groups")
    public ControllerResponse<List<ShippingGroup>> getShippingGroupList() {
        List<ShippingGroup> shippingGroups = shippingGroupService.queryAll();
        ControllerResponse<List<ShippingGroup>> resp =  ControllerResponse.ok().setData(shippingGroups);
        return resp;
    }

    // Get shipping group from api and store it to database
    @ApiOperation(value = "", notes = "Get shipping group by id using Metro API, and store it to the database.")
    @GetMapping("/groups/{id}")
    public ControllerResponse<ShippingGroup> getShippingGroupById(@PathVariable String id) {
        ShippingGroup shippingGroup = shippingGroupService.queryById(id);
        ControllerResponse<ShippingGroup> resp = ControllerResponse.ok().setData(shippingGroup);
        return resp;
    }

    @ApiOperation(value = "", notes = "Get shipping group from database by id.")
    @GetMapping("/groups/db-{id}")
    public ControllerResponse<ShippingGroup> getShippingGroupById_DB(@PathVariable String id) {
        List<String> sgs = new ArrayList<>();
        sgs.add(id);
        ShippingGroup shippingGroup = shippingGroupService.queryById(sgs).get(0);
        ControllerResponse<ShippingGroup> resp;
        if (shippingGroup == null) {
            resp = ControllerResponse.err(new RuntimeException("ShippingGroup does not exist in the database."));
        } else {
            resp = ControllerResponse.ok().setData(shippingGroup);
        }
        return resp;
    }


}
