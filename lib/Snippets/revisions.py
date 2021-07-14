doc = __revit__.ActiveUIDocument.Document


def revision_data(revision):
    print("SequenceNumber: "            + str( revision.SequenceNumber))
    print("NumberType: "                + str( revision.NumberType))
    print("RevisionDate: "              + str( revision.RevisionDate))
    print("Description: "               + str( revision.Description))
    print("Issued: "                    + str( revision.Issued))
    print("IssuedTo: "                  + str( revision.IssuedTo))
    print("IssuedBy: "                  + str( revision.IssuedBy))
    print("Visibility: "                + str( revision.Visibility))
    print("ViewSpecific: "              + str( revision.ViewSpecific))
    print("OwnerViewId: "               + str( revision.OwnerViewId))
    print("GroupId: "                   + str( revision.GroupId))
    print("AssemblyInstanceId: "        + str( revision.AssemblyInstanceId))
    print("GetDependentElements(): "    + str( revision.GetDependentElements()))

def revision_cloud_data(reivsion_cloud):
    print(reivsion_cloud)
    print("OwnerViewId: " + str( reivsion_cloud.OwnerViewId) )
    owner_view = doc.GetElement(reivsion_cloud.OwnerViewId)
    print("OwnerView: " + owner_view.Name)
    print("Hidden: " + str( reivsion_cloud.IsHidden(owner_view)))
